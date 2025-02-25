# csdn 资料处理类
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
class CsdnData:
    def __init__(self, driver):
        self.driver = driver

    #检查链接是否是csdn的文章链接
    def check_articleurl(self, url):
        if 'csdn.net' in url:
            return True
        if 't.csdnimg.cn'in url:
            return True
        return False

    def check_downloadurl(self, url):
        if 'download.csdn.net' in url:
            return True
        return False


    # 检查是否具备查看的文章权限
    def check_permission(self, page_source):
        if '订阅专栏 解锁全文' in page_source:
            return False
        return True

    # 检查是否具备下载权限
    def check_download(self, page_source):
        if "VIP专享下载" in page_source or "立即下载" in page_source:
            # 判断下载内容是否超过50MB
            file_size_span = self.driver.find_element(By.XPATH,
                                                 '/html/body/div[3]/div/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/span[7]')
            # 获取其中文本
            file_size = file_size_span.text
            # 判断其中是否含有 KB 或者MB 等单位
            if 'MB' in file_size:
                # 获取其中的数字
                file_size = float(file_size.replace('MB', '').strip())
                if file_size > 50:
                    raise RuntimeError("暂不支持下载文件超过50MB,如有需要可以联系管理员手动帮忙下载，微信：")
            elif 'KB' in file_size:
                pass
            else:
                # 判断下载内容是否超过50MB
                file_size_span = self.driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/span[6]')
                # 获取其中文本
                file_size = file_size_span.text
                if 'MB' in file_size:
                    # 获取其中的数字
                    file_size = float(file_size.replace('MB', '').strip())
                    if file_size > 50:
                        raise RuntimeError("暂不支持下载文件超过50MB,如有需要可以联系管理员手动帮忙下载，微信：")
            return True

    def try_download_file(self,logger):
        # 点击立即下载按钮
        try:
            download_button = self.driver.find_element(By.XPATH,
                                                       '/html/body/div[3]/div/div[1]/div/div[3]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/button/span/span')
            download_button.click()
        except Exception as e:
            logger.info("点击下载按钮出错，正在重试")
            download_button = self.driver.find_element(By.XPATH,
                                                       "/html/body/div[3]/div/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/button/span/span")
            download_button.click()
        logger.info("点击下载按钮")
        time.sleep(2)
        # 在弹窗页面中找到VIP专享下载按钮
        try:
            vip_download_button = self.driver.find_element(By.XPATH,
                                                           '/html/body/div[3]/div/div[1]/div/div[4]/div/div[3]/div/div/button')
            vip_download_button.click()
        except Exception as e:
            try:
                logger.info("点击VIP专享下载按钮出错，正在重试")
                vip_download_button = self.driver.find_element(By.XPATH,
                                                               "/html/body/div[3]/div/div[1]/div/div[3]/div/div[3]/div/div/button")
                vip_download_button.click()
            except Exception as e:
                logger.error(f"点击VIP专享下载按钮出错，错误内容为：{e}")
                self.driver.quit()
                os.system('taskkill /f /im chrome.exe')
                raise RuntimeError("Csdn账号今天已达到下载上限啦~ 该功能明天再开放! （文章浏览功能正常使用中）")
        logger.info("点击VIP专享下载按钮,开始下载文件...")
        time.sleep(3)


    def get_article(self, url,format,directory_path,logger):
        if not self.check_articleurl(url):
            raise RuntimeError("链接不是csdn的文章")
        self.driver.get(url)
        #获取请求后的页面源码
        page_source = self.driver.page_source
        #检查是否具备查看的文章权限
        check_permission = self.check_permission(page_source)
        if not check_permission:
            raise RuntimeError("专栏文章,没有查看文章的权限")
        ActionChains(self.driver).send_keys('aa').perform()
        time.sleep(3)
        ActionChains(self.driver).send_keys('sr').perform()
        time.sleep(2)
        if format == 'screenshot':
            # 获取目录中的所有文件和文件夹
            files_and_folders = os.listdir(directory_path)
            # 当前文件中的个数
            file_num = len(files_and_folders)
            ActionChains(self.driver).send_keys('pg').perform()
            # 由于导出图片功能不一定能够成功，所以需要计数  如果检查超过30秒仍然没有导出图片，那么就认为导出失败
            start_time = time.time()
            while True:
                files_and_folders = os.listdir(directory_path)
                if len(files_and_folders) > file_num:
                    break
                if time.time() - start_time > 30:
                    logger.info(f"导出图片失败")
                    raise RuntimeError("导出图片失败")
                time.sleep(1)
                logger.info(f"当前图片正在下载中...")

        else:
            ActionChains(self.driver).send_keys('oh').perform()
            time.sleep(3)



    def get_download(self,url,logger):
        # 检查url链接是否有问题
        if not self.check_downloadurl(url):
            raise RuntimeError("链接不是csdn的下载链接")
        #获取请求后的页面源码
        self.driver.get(url)
        # 获取请求后的页面源码
        page_source = self.driver.page_source
        # 检查页面是否具备下载的权限
        self.check_download(page_source)
        # 尝试下载文件
        self.try_download_file(logger)
