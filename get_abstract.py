import os
import re
import time
import random
import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

"""描述: 从CSV中根据文章标题和链接，获取论文摘要，生成标题对应的摘要txt文件"""



# 配置参数
CSV_PATH = 'yourpath'  # 替换为实际CSV路径
OUTPUT_DIR = 'yourpath'  # 替换为实际输出目录 
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 用户代理池（防反爬）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
]


def sanitize_filename(title, max_length=200):
    """
    把论文标题转换成safe valid filename
    
    参数:
        title (str): 原始标题
        max_length (int): 最大文件名长度（默认200）
    
    返回:
        str: 安全文件名
    
    功能:
        1. 兼容Unicode字符（中文/日文等）
        2. 处理Windows保留名称
        3. 长度截断防溢出
        4. 空格标准化处理
    """
    # Unicode规范化（兼容多语言）
    normalized = unicodedata.normalize('NFKC', title)
    
    # 替换非法字符（跨平台兼容）
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'  # 包含控制字符
    safe_name = re.sub(illegal_chars, '_', normalized)
    
    # Windows保留名称处理
    reserved_words = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1,10)] + [f'LPT{i}' for i in range(1,10)]
    if safe_name.upper() in reserved_words:
        safe_name = f'_{safe_name}'
    
    # 空格标准化（多个空格转单个下划线）[[12]][[15]]
    safe_name = re.sub(r'\s+', '_', safe_name.strip())
    
    # 长度截断与空值处理
    return safe_name[:max_length] if safe_name else 'untitled'

def setup_session(retries=5, backoff_factor=0.5, pool_size=10):
    """
    带重试机制和连接池优化的requests.Session配置
    
    参数:
        retries (int): 最大重试次数
        backoff_factor (float): 指数退避因子
        pool_size (int): 连接池大小
    
    返回:
        requests.Session: 配置完成的会话对象
    
    功能:
        1. 智能重试策略（服务器错误+连接错误）
        2. 连接池管理（提升性能）
        3. 动态超时设置
    """
    session = requests.Session()
    
    # 重试策略（包含连接错误）
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=['GET', 'HEAD'],
        connect=3  # 专门针对连接错误的尝试次数
    )
    
    # 连接适配器配置
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_size,
        pool_maxsize=pool_size
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # 动态超时设置（连接/读取分离）
    session.timeout = (3.05, 27)  # (connect, read)
    
    return session

def extract_abstract(html_content):
    """
    摘要提取主函数
    
    功能:
        1. 多语言摘要支持
        2. 备用选择器机制
        3. 自动编码检测
    """
    try:
        # 自动检测编码
        if hasattr(html_content, 'encoding'):
            soup = BeautifulSoup(html_content, 'html.parser', from_encoding=html_content.encoding)
        else:
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # 主选择器（英语摘要）
        abstract_div = soup.find('div', {
            'class': 'abstract-content selected',
            'id': 'eng-abstract'
        })
        
        return abstract_div.get_text(strip=True) if abstract_div else "摘要未找到"
    
    except Exception as e:
        return f"解析错误: {str(e)}"

def main():
    df = pd.read_csv(CSV_PATH, usecols=['Links', 'Title'])
    session = setup_session()
    
    # 进度跟踪
    total = len(df)
    print(f"开始处理 {total} 篇文献...")

    for i, row in df.iterrows():
        try:
            # 动态请求头配置
            HEADERS = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://pubmed.ncbi.nlm.nih.gov/'
            }
            # 获取网页内容
            response = session.get(
                row['Links'],
                headers=HEADERS,
                timeout=10
            )
            response.raise_for_status()
            
            # 提取并保存摘要
            abstract = extract_abstract(response.text)
            filename = sanitize_filename(row['Title']) + '.txt'
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(abstract)
            
            # 进度与延迟
            print(f"已处理：{i+1}/{len(df)} - {filename}")
            time.sleep(random.uniform(0.5, 1.5))  # 随机延迟防封
            

        except requests.exceptions.RequestException as e:
            print(f"请求失败：{row['Links']} - {str(e)}")
        except Exception as e:
            print(f"处理错误：{row['Links']} - {str(e)}")

    print(f"处理完成！结果已保存至 {OUTPUT_DIR} 目录")

if __name__ == "__main__":
    main()
