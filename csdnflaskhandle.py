import subprocess
import sys
from flask import Flask, request, jsonify
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from article import CsdnData

from selenium.webdriver.chrome.options import Options
import logging
import configparser
import osutils

config = configparser.ConfigParser()
config.read('config.ini',encoding='utf-8')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 创建流处理器
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# 将处理器添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

app = Flask(__name__)



@app.route('/csdn/article/download', methods=['POST'])
def article_download():
    logger.info("当前请求参数是："+str(request.get_json()))
    try:
        if request.content_type == 'application/json':
            # 处理JSON格式的数据
            data = request.get_json()
            article_url = data.get('article_url')
            download_url = data.get('download_url')
            receiver_email = data.get('receiver_email')
            format = data.get('format')
            # 创建一个Chrome选项对象
            chrome_options = Options()
            service = Service(config['DEFAULT']['ChromeDriverPath'])
            #启动本地Chrome浏览器 不启动无痕方式 (直接避过登录)
            chrome_options.add_argument(f'user-data-dir={config['DEFAULT']['WindowsProfilePath']}')
            driver = webdriver.Chrome(options=chrome_options,service=service)
            directory_path = config['DEFAULT']['DirectoryPath']
            try:
                csdnData = CsdnData(driver)
                # 根据类型 判断是下载文章还是下载资源
                if article_url:
                    csdnData.get_article(article_url,format,directory_path,logger)
                else:
                    csdnData.get_download(download_url,logger)
                # 下载完成后发送邮件
                if osutils.is_download_completed(directory_path, logger):
                    latest_file_path = osutils.get_latest_file(directory_path, logger)
                    #发送邮件
                    osutils.send_mail(config['DEFAULT']['Email'],config['DEFAULT']['AuthCode'],receiver_email,latest_file_path,logger)
                driver.quit()
            except RuntimeError as runtimeError:
                logger.error(f"下载文章失败,错误内容为：{runtimeError}")
                driver.quit()
                osutils.send_error_mail(config['DEFAULT']['Email'], config['DEFAULT']['AuthCode'], receiver_email,
                                        str(runtimeError), logger)
                return str(runtimeError), 504
            return '下载完毕，已发送至邮箱，请查收！', 200
        else:
            return '提交数据格式不正确',403
    except Exception as e:
        logger.error(f"下载文章失败,错误内容为：{e}")
        # 发送邮件
        osutils.send_mail(config['DEFAULT']['Email'], config['DEFAULT']['AuthCode'], receiver_email, "下载异常，请联系管理员解决",
                          logger)
        return "下载异常，请联系管理员解决", 503
    finally:
        # 杀掉Chrome进程确保下一次请求不受影响
        os.system('taskkill /f /im chrome.exe')



if __name__ == '__main__':
    # 定义需要安装的模块列表
    required_packages = ['flask', 'requests','selenium']
    # 检查每个模块是否已安装，未安装的将使用pip安装
    for package in required_packages:
        try:
            # 尝试导入模块
            __import__(package)
        except ImportError:
            # 如果模块未安装，使用pip安装
            print(f"安装模块：{package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    app.run(host='0.0.0.0',debug=True,port=5000)
