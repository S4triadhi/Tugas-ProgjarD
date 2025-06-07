from socket import *
import threading
import logging
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            data = ""
            while True:
                recv_data = self.connection.recv(1024)
                if recv_data:
                    data += recv_data.decode()
                    if "\r\n\r\n" in data:
                        break
                else:
                    break
            response = fp.proses_string(data.strip()) + "\r\n\r\n"
            self.connection.sendall(response.encode())
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=58000):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket(AF_INET, SOCK_STREAM)
        self.my_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(1)
        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"connection from {client_address}")
            client_thread = ProcessTheClient(connection, client_address)
            client_thread.start()
            self.the_clients.append(client_thread)

def main():
    svr = Server()
    svr.start()

if __name__ == '__main__':
    main()
