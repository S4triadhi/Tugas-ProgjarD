import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    try:
        rcv = ""
        while True:
            data = connection.recv(1024)
            if not data:
                break
            rcv += data.decode()
            if '\r\n\r\n' in rcv:
                # cek jika ada Content-Length (POST)
                headers, body = rcv.split('\r\n\r\n', 1)
                content_length = 0
                for line in headers.split('\r\n'):
                    if line.lower().startswith('content-length:'):
                        content_length = int(line.split(':')[1].strip())
                # jika POST dan belum lengkap, terus baca
                while len(body) < content_length:
                    data = connection.recv(1024)
                    if not data:
                        break
                    body += data.decode()
                break

        hasil = httpserver.proses(rcv)
        hasil += b"\r\n\r\n"
        connection.sendall(hasil)
    except Exception as e:
        logging.warning(f"Error processing client {address}: {e}")
    finally:
        connection.close()

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(5)
    print("Server running on port 8885...")

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            print(f"Connection from {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)

def main():
    Server()

if __name__ == "__main__":
    main()
