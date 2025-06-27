import socket
import ssl
import os
import logging

# Server Address (gunakan salah satu)
# server_address = ('172.16.16.101', 8885)  # Thread Pool
server_address = ('172.16.16.101', 8889)  # Process Pool

def make_socket(addr, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        return sock
    except Exception as e:
        logging.warning(f"Socket error: {e}")
        return None

def make_secure_socket(addr, port):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.connect((addr, port))
        return context.wrap_socket(raw_sock, server_hostname=addr)
    except Exception as e:
        logging.warning(f"Secure socket error: {e}")
        return None

def read_http_response(sock):
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        data = sock.recv(1024)
        if not data:
            break
        buffer += data

    if b"\r\n\r\n" not in buffer:
        return "Invalid HTTP response"

    header_part, body = buffer.split(b"\r\n\r\n", 1)
    headers = header_part.decode().split("\r\n")
    content_length = 0
    for line in headers:
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())

    # Read remaining body if content-length > len(body)
    while len(body) < content_length:
        data = sock.recv(1024)
        if not data:
            break
        body += data

    return header_part.decode() + "\r\n\r\n" + body.decode(errors='ignore')

def send_request(request_str, secure=False):
    sock = make_secure_socket(*server_address) if secure else make_socket(*server_address)
    if not sock:
        print("Gagal membuat koneksi.")
        return
    try:
        sock.sendall(request_str.encode())
        response = read_http_response(sock)
        print("\n--- Response dari Server ---\n")
        print(response)
    except Exception as e:
        logging.warning(f"Error receiving data: {e}")
    finally:
        sock.close()

def list_files():
    req = "GET /list HTTP/1.0\r\n\r\n"
    send_request(req)

def upload_file():
    filename = input("Masukkan nama file yang akan diupload: ").strip()
    if not os.path.exists(filename):
        print("File tidak ditemukan.")
        return
    with open(filename, 'r') as f:
        content = f.read()
    req = (
        f"POST /upload/{filename} HTTP/1.0\r\n"
        f"Content-Length: {len(content.encode())}\r\n"
        f"Content-Type: text/plain\r\n"
        f"\r\n"
        f"{content}"
    )
    send_request(req)

def delete_file():
    filename = input("Masukkan nama file yang akan dihapus: ").strip()
    req = f"GET /delete/{filename} HTTP/1.0\r\n\r\n"
    send_request(req)

def main():
    while True:
        print("\n=== MENU ===")
        print("1. List Semua File")
        print("2. Upload File")
        print("3. Hapus File")
        print("4. EXIT")
        try:
            pilihan = int(input("Pilih opsi (1-4): "))
            if pilihan == 1:
                list_files()
            elif pilihan == 2:
                upload_file()
            elif pilihan == 3:
                delete_file()
            elif pilihan == 4:
                print("Terima kasih. Keluar.")
                break
            else:
                print("Pilihan tidak valid.")
        except ValueError:
            print("Input harus berupa angka.")

if __name__ == "__main__":
    main()
