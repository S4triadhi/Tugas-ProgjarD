import json
import logging
import shlex
from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            c = shlex.split(string_datamasuk)
            request = c[0].lower()
            params = c[1:]
            if hasattr(self.file, request):
                result = getattr(self.file, request)(params)
                return json.dumps(result)
            else:
                return json.dumps(dict(status='ERROR', data='request tidak dikenali'))
        except Exception as e:
            return json.dumps(dict(status='ERROR', data=str(e)))
