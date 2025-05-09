import requests
import re
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import time

from fastapi import Body # 导入 Body
from app.plugins import _PluginBase
from app.db.downloadhistory_oper import DownloadHistoryOper
from app.core.context import Context, MediaInfo, TorrentInfo
from app.helper.downloader import DownloaderHelper
from app.helper.service import ServiceConfigHelper
from app.schemas.types import SystemConfigKey
from app.schemas.system import TransferDirectoryConf
from app.modules.themoviedb.tmdbapi import TmdbApi

# 定义磁力下载请求体模型
class MagnetDownloadRequest(BaseModel):
    magnet_link: str
    download_dir: Optional[str] = None
    title: str # 添加 title 字段
    des: Optional[str] = None # 添加 des 字段

# --- Add Pydantic model for config ---
class Site6VSupportConfig(BaseModel):
    enable: bool = False
    notify: bool = False
    cron: str = '30 3 * * *'
    onlyonce: bool = False

class Site6VSupport(_PluginBase):
    # 插件名称
    plugin_name = "6v站点支持"
    # 插件描述
    plugin_desc = "6v站点搜索与下载"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/xiaoziguys/MoviePilot-Plugins/main/icons/6v.png"
    # 插件版本
    plugin_version = "0.0.6"
    # 插件作者
    plugin_author = "xiaoziguys"
    # 作者主页
    author_url = "https://github.com/xiaozigusy"
    # 插件配置项ID前缀
    plugin_config_prefix = "site6v_"
    # 加载顺序
    plugin_order = 50
    # 可使用的用户级别
    auth_level = 1

    _enable = False
    _cron = '30 3 * * *'
    _selected_ids: List[str] = []
    _notify = False
    _onlyonce = False

    def init_plugin(self, config: dict = None):

        if config:
            self._enable = config.get('enable', False)
            self._selected_ids = config.get('selected_ids', [])
            self._cron = config.get('cron', '30 3 * * *')
            self._notify = config.get('notify', False)
            self._onlyonce = config.get('onlyonce', False)

        self.base_url = "https://www.66s6.net/"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "tinmklastsearchtime=1733461568"
        }
        self.timeout = 10

    def _decode_filename(self, encoded_str: str) -> str:
        try:
            decoded_str = encoded_str.encode('latin1').decode('utf-8')
            return decoded_str
        except Exception as e:
            return f"解码失败: {str(e)}"
    
    def _get_download_links(self, link: str) -> Optional[List[Dict[str, Any]]]:
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
                        'des': self._decode_filename(link.text.strip()),
                        'url': link['href']
                    })
            return results if results else None
        except requests.exceptions.RequestException as e:
            print(f"搜索请求出错: {e}")
            return None
        except Exception as e:
            print(f"解析HTML出错: {e}")
            return None

    def _search(self, query: str) -> Optional[List[Dict[str, Any]]]:
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
                    for link in self._get_download_links(detail_link['href']):
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
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题中的季数信息，如[第二季]
        """
        if not title:
            return title
        return re.sub(r'\[.*?\]', '', title).strip()

    def _get_tmdb_info(self, title: str) -> dict:
        """
        使用清理后的标题查询TMDB信息
        """
        tmdb = TmdbApi()
        results = tmdb.search_multiis(title)
        if results:
            for result in results:
                if result['title'] == title:
                    return result
        return {}

    def _add_magnet_download(self, request: MagnetDownloadRequest) -> Dict[str, Any]:
        """
        通过磁力链接添加下载任务
        :param request: 磁力下载请求体
        :return: 结果字典
        """
        downloader_helper = DownloaderHelper() # 实例化 DownloaderHelper
        
        # 获取所有下载器服务
        downloader_services = downloader_helper.get_services()
        
        default_downloader_instance = None
        downloader_name = None
        # 查找默认下载器实例
        for service_info in downloader_services.values():
            if service_info.config and service_info.config.default:
                default_downloader_instance = service_info.instance
                downloader_name = service_info.name # 获取下载器名称
                break

        if not default_downloader_instance:
            return {"success": False, "message": "未找到默认下载器，请检查下载器配置！"}

        try:
            success = default_downloader_instance.add_torrent(content=request.magnet_link, tag=['6v', 'MOVIEPILOT'], download_dir=request.download_dir)
        except Exception as e:
            return {"success": False, "message": f"下载任务添加失败，错误信息：{str(e)}"}

        if success:
            download_hash = None
            if hasattr(default_downloader_instance, 'get_torrent_id_by_tag'):
                 download_hash = default_downloader_instance.get_torrent_id_by_tag(tags='6v')
                 if download_hash:
                     print(f"成功获取下载任务哈希值: {download_hash} 使用标签 '6v'")
                 else:
                     print("未能通过标签 '6v' 获取下载任务哈希值")

            if download_hash:
                # 登记下载历史记录
                downloadhis_oper = DownloadHistoryOper()
                # 构建一个简化的Context对象，只包含必要的信息
                # 从 des 字段中提取季数和集数
                seasons = None
                episodes = None
                if request.des:
                    # 尝试匹配包含季数和集数的格式，例如：S01E06
                    match = re.search(r'S(\d{1,2})E(\d{1,2})', request.des, re.IGNORECASE)
                    if match:
                        seasons = int(match.group(1))
                        episodes = int(match.group(2))
                    else:
                        # 如果不包含季数，设为第一季
                        seasons = 1

                # 清理标题中的季数信息
                cleaned_title = self._clean_title(request.title)
                
                # 使用清理后的标题查询TMDB信息
                tmdb_info = self._get_tmdb_info(cleaned_title)
                
                # 使用查询结果构建MediaInfo
                media_type = "unknown"
                tmdbid = None
                year = None
                image = None
                if tmdb_info:
                    media_type = "tv" if tmdb_info.get('media_type') == 'TV' else "movie"
                    tmdbid = tmdb_info.get('id')
                    year = tmdb_info.get('first_air_date', '').split('-')[0] if media_type == "tv" else tmdb_info.get('release_date', '').split('-')[0]
                    image = f"https://image.tmdb.org/t/p/original{tmdb_info.get('poster_path')}" if tmdb_info.get('poster_path') else None
                
                downloadhis_oper.add(
                    path=request.download_dir or "", # 使用下载目录作为路径
                    type=media_type, # 使用查询到的媒体类型
                    title=cleaned_title, # 使用清理后的标题
                    year=year,
                    tmdbid=tmdbid,
                    imdbid=None,
                    tvdbid=None,
                    doubanid=None,
                    seasons=seasons, # 设置季数
                    episodes=episodes, # 设置集数
                    image=image,
                    downloader=downloader_name, # 下载器名称
                    download_hash=download_hash, # 下载任务hash
                    torrent_name=request.title, # 种子名称使用原始标题
                    torrent_description=request.des, # 使用描述作为种子描述
                    torrent_site="6v", # 站点设置为6v
                    userid=None, # 用户ID未知
                    username="plugin_site6vsupport", # 用户名设置为插件名
                    channel=None,
                    date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    media_category=None,
                    episode_group=None,
                    note={"source": "site6v_magnet_download"} # 来源标记
                )

            return {"success": True, "message": "下载任务添加成功！"}
        else:
            return {"success": False, "message": "下载任务添加失败，请检查下载器配置或网络连接！"}
        
    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """Returns None for Vue form, but provides initial config data."""
        # This dict is passed as initialConfig to Config.vue by the host
        return None, self._get_config()

    def get_page(self) -> Optional[List[dict]]:
        """Vue mode doesn't use Vuetify page definitions."""
        return None

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        # 返回插件的启用状态
        return self._enable

    def stop_service(self):
        """
        停止插件服务
        """
        # 在这里添加停止插件服务的逻辑，如果需要的话
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        return [{
            "path": "/search_from_6v",
            "endpoint": self._search,
            "methods": ["GET"],
            "auth": "bear",
            "summary": "从6v搜索资源",
            "description": "从6v搜索资源",
        },
        {
            "path": "/add_magnet_download",  # 新增磁力链接下载路由
            "endpoint": self._add_magnet_download, # 指向新的方法
            "methods": ["POST"], # 使用POST方法
            "auth": "bear",
            "summary": "添加磁力链接下载任务",
            "description": "添加磁力链接下载任务",
        },
        {
            "path": "/get_transfer_directories", # 新增获取文件整理目录路由
            "endpoint": self._get_transfer_directories, # 指向新的方法
            "methods": ["GET"], # 使用GET方法
            "auth": "bear",
            "summary": "获取文件整理目录列表",
            "description": "获取文件整理目录列表",
        }]
    
    # --- V2 Vue Interface Method ---
    @staticmethod
    def get_render_mode() -> Tuple[str, Optional[str]]:
        """Declare Vue rendering mode and assets path."""
        return "vue", "dist/assets"

    # --- Other Base Methods ---
    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [] # No commands defined for this plugin

    def _get_transfer_directories(self) -> List[Dict[str, Any]]:
        """
        获取文件整理目录列表
        :return: 文件整理目录列表
        """
        # 使用 ServiceConfigHelper 获取 TransferDirectoryConf 配置
        configs: List[TransferDirectoryConf] = ServiceConfigHelper.get_configs(
            SystemConfigKey.Directories, TransferDirectoryConf
        )
        # 提取目录信息
        directories = []
        for config in configs:
            if config.download_path:
                directories.append({
                    "name": config.name or config.download_path, # 使用名称或路径作为显示名称
                    "path": config.download_path
                })
        return directories
