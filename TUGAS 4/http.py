import os
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ] + [f"{k}:{v}\r\n" for k, v in headers.items()] + ["\r\n"]

        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        return ''.join(resp).encode() + messagebody

    def proses(self, data):
        try:
            header_part, body_part = data.split("\r\n\r\n", 1)
        except ValueError:
            return self.response(400, 'Bad Request', 'Invalid HTTP format', {})

        lines = header_part.split("\r\n")
        if not lines:
            return self.response(400, 'Bad Request', '', {})

        baris = lines[0]
        all_headers = [n for n in lines[1:] if n != '']

        try:
            method, path, *_ = baris.split()
            method = method.upper()
            if method == 'GET':
                return self.http_get(path, all_headers)
            elif method == 'POST':
                return self.http_post(path, all_headers, body_part)
            else:
                return self.response(405, 'Method Not Allowed', '', {})
        except Exception as e:
            return self.response(400, 'Bad Request', str(e), {})

    def http_get(self, object_address, headers):
        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah Web Server Percobaan', {})
        if object_address == '/list':
            files = os.listdir('./')
            files_list = '\n'.join(files)
            return self.response(200, 'OK', files_list, {'Content-Type': 'text/plain'})
        if object_address.startswith('/delete/'):
            filename = object_address.split('/delete/')[1]
            if os.path.exists(filename):
                os.remove(filename)
                return self.response(200, 'OK', f"File '{filename}' deleted.", {'Content-Type': 'text/plain'})
            else:
                return self.response(404, 'Not Found', f"File '{filename}' tidak ditemukan", {'Content-Type': 'text/plain'})

        filename = object_address.lstrip('/')
        if not os.path.exists(filename):
            return self.response(404, 'Not Found', f"File '{filename}' tidak ditemukan", {})
        with open(filename, 'rb') as f:
            content = f.read()
        ext = os.path.splitext(filename)[1]
        content_type = self.types.get(ext, 'application/octet-stream')
        return self.response(200, 'OK', content, {'Content-Type': content_type})

    def http_post(self, object_address, headers, body):
        if object_address.startswith('/upload/'):
            filename = object_address.split('/upload/')[1]
            try:
                with open(filename, 'w') as f:
                    f.write(body)
                return self.response(200, 'OK', f"File '{filename}' uploaded.", {'Content-Type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e), {})
        return self.response(400, 'Bad Request', '', {})

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET testing.txt HTTP/1.0')
	print(d)
	d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
#	d = httpserver.http_get('testing.txt')
#	print(d)
