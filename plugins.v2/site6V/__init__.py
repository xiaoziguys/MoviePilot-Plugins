import requests
import sys
from bs4 import BeautifulSoup

class Site6V:
    # 插件名称
    plugin_name = "6v站点"
    # 插件描述
    plugin_desc = "6v站点搜索与下载"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/xiaoziguys/MoviePilot-Plugins/main/icons/6v.png"
    # 插件版本
    plugin_version = "0.1"
    # 插件作者
    plugin_author = "xiaoziguys"
    # 作者主页
    author_url = "https://github.com/xiaozigusy"
    # 插件配置项ID前缀
    plugin_config_prefix = "logsclean_"
    # 加载顺序
    plugin_order = 50
    # 可使用的用户级别
    auth_level = 1

    def __init__(self):
        self.base_url = "https://www.66s6.net/"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "tinmklastsearchtime=1733461568"
        }
        self.timeout = 10

    def decode_filename(self, encoded_str):
        try:
            decoded_str = encoded_str.encode('latin1').decode('utf-8')
            return decoded_str
        except Exception as e:
            return f"解码失败: {str(e)}"
    
    def get_download_links(self, link):
        try:
            response = requests.get(
                f"{self.base_url}{link}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 尝试解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for item in soup.find_all('tr'):
                link = item.find('a')
                if link:
                    results.append({
                        'des': self.decode_filename(link.text.strip()),
                        'url': link['href']
                    })
            return results if results else None
        except requests.exceptions.RequestException as e:
            print(f"搜索请求出错: {e}")
            return None
        except Exception as e:
            print(f"解析HTML出错: {e}")
            return None

    def search(self, query):
        """
        搜索功能
        :param query: 搜索关键词
        :return: 搜索结果
        """
        payload = {
            "show": "title",
            "tempid": 1,
            "tbname": "article",
            "mid": 1,
            "dopost": "search",
            "submit": "",
            "keyboard": query
        }
        try:
            response = requests.post(
                f"{self.base_url}/e/search/1index.php",
                data=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 尝试解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            # 假设搜索结果在某个特定的HTML元素中，这里需要根据实际HTML结构调整
            for item in soup.find_all('div', class_='article'):
                detail_link = item.find('a')
                if detail_link:
                    for link in self.get_download_links(detail_link['href']):
                        results.append({
                        'title': detail_link.text.strip(),
                        'url': link['url'],
                        'des': link['des']
                    })
            return results if results else None
        except requests.exceptions.RequestException as e:
            print(f"搜索请求出错: {e}")
            return None
        except Exception as e:
            print(f"解析HTML出错: {e}")
            return None
        
    def get_api(self):
        return [{
            "path": "/searchFrom6V",
            "endpoint": self.search,
            "methods": ["GET"],
            "summary": "从6v搜索资源",
            "description": "从6v搜索资源",
        }]
