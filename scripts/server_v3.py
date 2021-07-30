"""
响应静态界面，和 /plain.html 配合使用
"""

#-*- coding:utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, os


class ServerException(Exception):
    '''服务器内部错误'''
    pass

class RequestHandler(BaseHTTPRequestHandler):
    '''处理请求并返回页面'''

    # 错误页面模板
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
    """


    # 处理一个GET请求
    def do_GET(self):
        try:
            # 完整路径
            full_path = os.getcwd() + self.path + "plain.html"
            print(full_path)

            # 该路径不存在...
            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))
            
            # 该路径是一个文件
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            
            # 该路径压根儿不是一个文件
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))

        # 处理异常
        except Exception as msg:
            self.handle_error(msg)


    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read:{1}".format(self.path, msg)
            self.handle_error(msg)

    
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'), 404)
    

    def create_page(self):
        values = {
            'date_time'   : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command'     : self.command,
            'path'        : self.path
        }
        page = self.Page.format(**values)
        return page


    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        # 由于 handle_error 函数中的 content 内容被编码为二进制
        # 所以 send_content 函数中的 page 需要取消二进制编码
        # self.wfile.write(self.Page.encode('utf-8'))
        self.wfile.write(content)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()