# 运行：mitmweb -s E:\obsidian\Master\fund_stream_project\codes\spider\mitm_script.py
# 打开代理，8080端口

from mitmproxy import http
import os
mitm_file_path=r'E:\obsidian\Master\fund_stream_project\codes\spider\mitm_url.txt'
class MyAddon:
    def response(self, flow: http.HTTPFlow) -> None:
        if ".m3u8" in flow.request.url:
            if not os.path.exists(mitm_file_path):
                with open(mitm_file_path, "a") as file:
                    # 获取 flow.request.pretty_url
                    url_to_write = flow.request.url
                    # 写入到文件
                    file.write(url_to_write+"\n")
                file.close()

    # def request(flow: http.HTTPFlow) -> None:
    # # 检查请求是否为.m3u8文件
    #     if flow.request.path.endswith(".m3u8"):

    #     # 打印请求的 URL
    #         if not os.path.exists(mitm_file_path):
    #             with open(mitm_file_path, "a") as file:
    #                 # 获取 flow.request.pretty_url
    #                 url_to_write = flow.request.url
    #                 # 写入到文件
    #                 file.write(url_to_write+"\n")
    #             file.close()

addons = [
    MyAddon()
]