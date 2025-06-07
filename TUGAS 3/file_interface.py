import os
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        os.makedirs('files', exist_ok=True)
        os.chdir('files/')

    def list(self, params=[]):
        try:
            return dict(status='OK', data=glob('*.*'))
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        if not params or params[0] == '':
            return dict(status='ERROR', data='parameter tidak lengkap')
        try:
            filename = params[0]
            with open(filename, 'rb') as f:
                content = base64.b64encode(f.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=content)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        if len(params) < 2 or params[0] == '' or params[1] == '':
            return dict(status='ERROR', data='parameter tidak lengkap')
        try:
            filename = params[0]
            filedata = base64.b64decode(params[1])
            with open(filename, 'wb') as f:
                f.write(filedata)
            return dict(status='OK', data='File berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        if not params or params[0] == '':
            return dict(status='ERROR', data='parameter tidak lengkap')
        try:
            filename = params[0]
            os.remove(filename)
            return dict(status='OK', data='File berhasil dihapus')
        except Exception as e:
            return dict(status='ERROR', data=str(e))
