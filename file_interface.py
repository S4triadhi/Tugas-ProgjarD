import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self, folder="files"):
        self.folder = folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        os.chdir(self.folder)

    def list_files(self):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get_file(self, params=[]):
        try:
            if not params:
                return dict(status='ERROR', data='parameter tidak lengkap')
            filename = params[0]
            with open(filename, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload_file(self, params=[]):
        """
        upload <nama_file> <content_base64>
        """
        try:
            if len(params) < 2:
                return dict(status='ERROR', data='parameter tidak lengkap')
            filename, filedata_b64 = params[0], params[1]
            with open(filename, 'wb') as fp:
                fp.write(base64.b64decode(filedata_b64))
            return dict(status='OK', data=f'file "{filename}" berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete_file(self, params=[]):
        """
        delete <nama_file>
        """
        try:
            if not params:
                return dict(status='ERROR', data='parameter tidak lengkap')
            filename = params[0]
            os.remove(filename)
            return dict(status='OK', data=f'file "{filename}" berhasil dihapus')
        except Exception as e:
            return dict(status='ERROR', data=str(e))


# Example usage
if __name__ == '__main__':
    fm = FileInterface()

    print("=== LIST FILES ===")
    print(json.dumps(fm.list_files(), indent=2))

    print("\n=== GET FILE ===")
    print(json.dumps(fm.get_file(['pokijan.jpg']), indent=2))

    # Example for upload:
    # encoded = base64.b64encode(open("test.txt", "rb").read()).decode()
    # print(json.dumps(fm.upload_file(['test_uploaded.txt', encoded]), indent=2))

    # Example for delete:
    # print(json.dumps(fm.delete_file(['test_uploaded.txt']), indent=2))
