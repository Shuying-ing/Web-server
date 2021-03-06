"""
在根 url 显示首页内容，和 /plain.html 配合使用
每一种情况都单独写成一个条件类
"""

#-*- coding:utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, os


class ServerException(Exception):
    '''服务器内部错误'''
    pass


class case_no_file(object):
    '''该路径不存在'''
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_existing_file(object):
    '''该路径是一个文件'''
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    
    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_directory_index_file(object):
    '''该路径是一个文件夹'''
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    #判断目标路径是否是目录&&目录下是否有index.html
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    #响应index.html的内容
    def act(self, handler):
        handler.handle_file(self.index_path(handler))


class case_always_fail(object):
    '''该路径压根儿不是一个文件'''
    def test(self, handler):
        return True
     
    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path)) 


class RequestHandler(BaseHTTPRequestHandler):
    '''
    请求路径合法则返回相应处理
    否则返回错误页面
    '''

    Cases = [case_no_file(),
    case_existing_file(),
    case_directory_index_file(),
    case_always_fail()]

    # 错误页面模板
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
    """


    def do_GET(self):
        try:
            self.path = "/plain.html"
            self.full_path = os.getcwd() + self.path
            print(self.full_path)

            # 遍历所有情况并处理
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

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
    

    # 发送数据到客户端
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()