import os
import requests
import re
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s,%(message)s',  # 去掉毫秒
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.StreamHandler(),  # 输出到终端
                        logging.FileHandler("run_log.txt", mode='a', encoding='utf-8')  # 保存日志到文件，使用UTF-8编码
                    ])
logger = logging.getLogger()

# 文件路径
version_file = 'Version.txt'

# 获取当前版本号
def get_current_version():
    url = 'https://www.graphicode.com/download/GC-PowerStation'
    try:
        logger.info('正在获取网页内容...')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        version_text = soup.select_one('section#download > div > div:nth-of-type(2) > table > tbody > tr:nth-of-type(2) > td > h2 > a')

        if version_text:
            # 正则表达式提取版本号
            match = re.search(r'Version (\d+\.\d+)', version_text.get_text())
            if match:
                current_version = match.group(1)
                logger.info(f'当前版本号：{current_version}')
                return current_version
            else:
                logger.error('未找到有效的版本号')
                return None
        else:
            logger.error('未找到版本号')
            return None
    except Exception as e:
        logger.error(f'获取版本号失败: {e}')
        return None

# 获取已保存的版本号
def get_saved_version():
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            saved_version = f.read().strip()
            logger.info(f'已保存版本号：{saved_version}')
            return saved_version
    return None

# 保存当前版本号到 Version.txt
def save_version(version):
    with open(version_file, 'w') as f:
        f.write(version)
    logger.info(f'保存当前版本号 {version} 到 Version.txt')

# 下载包
def download_package(version, language):
    # 根据语言选择下载链接
    urls = {
        'english': [
            'https://cdn.graphicode.com/pubs/powerplatform.zip',
            'https://cdn.graphicode.com/pubs/powerplatform_x64.zip'
        ],
        'simplified_chinese': [
            'https://cdn.graphicode.com/pubs/PPSimpChi.zip',
            'https://cdn.graphicode.com/pubs/PPSimpChi_x64.zip'
        ],
        'traditional_chinese': [
            'https://cdn.graphicode.com/pubs/PPTradChi.zip',
            'https://cdn.graphicode.com/pubs/PPTradChi_x64.zip'
        ]
    }

    if language not in urls:
        logger.error(f'不支持的语言：{language}')
        return

    # 创建目录
    folder = os.path.join(version, language)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 下载文件
    for url in urls[language]:
        filename = os.path.join(folder, url.split('/')[-1])
        logger.info(f'从 {url} 下载到 {filename}')
        try:
            urllib.request.urlretrieve(url, filename)
            logger.info(f'下载完成：{filename}')
        except Exception as e:
            logger.error(f'下载失败 {filename}: {e}')

# 主函数
def main():
    current_version = get_current_version()
    if current_version is None:
        return

    saved_version = get_saved_version()

    if saved_version != current_version:
        if saved_version:
            logger.info(f'版本号不匹配，保存当前版本号 {current_version} 到 Version.txt')
        else:
            logger.info(f'未找到已保存版本，第一次运行')
        
        save_version(current_version)

        # 下载简体中文、繁体中文和英语版本
        for language in ['simplified_chinese', 'traditional_chinese', 'english']:
            download_package(current_version, language)
    else:
        logger.info(f'当前版本已是最新版本：{current_version}')

if __name__ == '__main__':
    main()
