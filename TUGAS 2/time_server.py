from socket import *
import socket
import threading
import logging
import time
import sys

# Konfigurasi logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# ========================================
# b. Server dapat melayani request concurrent (multithreading)
#    dengan membuat thread ClientHandler untuk setiap koneksi klien
# ========================================
class ClientHandler(threading.Thread):  # <-- Ganti nama class di sini
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break

                # Menghapus karakter \r\n dari akhir string
                message = data.decode('utf-8').strip()

                # ========================================
                # c.i. Request diawali dengan "TIME" diakhiri \r\n
                # d. Server merespon dengan:
                #    i. UTF-8
                #    ii. Diawali dengan "JAM"
                #    iii. Format jam "hh:mm:ss" dan diakhiri dengan \r\n
                # ========================================
                if message.startswith("TIME"):
                    current_time = time.strftime("%H:%M:%S")
                    response = f"JAM {current_time}\r\n"  # format jam sesuai poin d
                    self.connection.sendall(response.encode('utf-8'))  # kirim dalam UTF-8

                # ========================================
                # c.ii. Request dapat diakhiri dengan "QUIT" diakhiri \r\n
                # ========================================
                elif message.startswith("QUIT"):
                    break

                else:
                    # Jika perintah tidak dikenali
                    self.connection.sendall(b"Invalid command\r\n")

        except Exception as e:
            logging.warning(f"Exception in client thread: {e}")

        finally:
            self.connection.close()
            logging.warning(f"Connection closed: {self.address}")

# ========================================
# a. Membuka port 45000 dengan transport TCP
#    - socket.AF_INET untuk IPv4
#    - socket.SOCK_STREAM untuk TCP
# ========================================
class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # <-- a. TCP socket
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('172.16.16.101', 45000))  # <-- a. Bind ke port 45000
        self.my_socket.listen(5)  # Listen untuk koneksi masuk
        logging.warning("Server is listening on port 45000...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"Connection from {client_address}")
            
            # b. Setiap koneksi klien ditangani oleh thread terpisah
            handler = ClientHandler(connection, client_address) 
            handler.start()
            self.the_clients.append(handler)

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
