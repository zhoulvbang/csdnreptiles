import os
import time

from csdnreptiles.qqemail import QQMailer


# 检查下载是否完成
def is_download_completed(download_dir,logger):
    # 循环检查下载文件夹中是否还有临时文件
    while any([filename.endswith(".crdownload") for filename in os.listdir(download_dir)]):
        # 找到存在的crdownload文件
        for filename in os.listdir(download_dir):
            if filename.endswith(".crdownload"):
                logger.info(f"存在crdownload文件: {filename} 下载中...")
        time.sleep(1)  # 等待1秒再次检查
    return True


# 获取目录中最新的文件
def get_latest_file(directory_path,logger):
    # 获取目录中的所有文件和文件夹
    files_and_folders = os.listdir(directory_path)
    # 过滤出文件列表
    files = [f for f in files_and_folders if os.path.isfile(os.path.join(directory_path, f))]
    # 初始化最新文件的时间戳和路径
    latest_timestamp = 0
    latest_file_path = None
    # 遍历文件列表，找到最新生成的文件
    for file in files:
        file_path = os.path.join(directory_path, file)
        file_timestamp = os.path.getmtime(file_path)  # 获取文件最后修改时间的时间戳
        if file_timestamp > latest_timestamp:
            latest_timestamp = file_timestamp
            latest_file_path = file_path
    # 打印最新生成的文件路径
    logger.info(f"最新生成的文件路径: {latest_file_path}")
    return latest_file_path

# 发送邮件
def send_mail(sender,auth_code,receiver_email,latest_file_path,logger):
    mailer = QQMailer(sender, auth_code)
    mailer.send_mail(
        receiver_email=receiver_email,
        subject="csdn资源助手",
        body="csdn文章资源自助服务内容，请在附件中查看您的文章内容",
        attachment_path=latest_file_path
    )
    logger.info("邮件发送成功！")


def send_error_mail(sender,auth_code,receiver_email,notes,logger):
    mailer = QQMailer(sender, auth_code)
    mailer.send_mail(
        receiver_email=receiver_email,
        subject="csdn资源助手",
        body="csdn文章资源自助服务内容，下载失败,失败原因:"+notes,
    )
    logger.info("已邮件通知下载失败!")