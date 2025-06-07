import socket
import json
import base64
import logging

server_address = ('172.16.16.101', 58000)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        # tambahkan \r\n\r\n sebagai delimiter
        sock.sendall((command_str + "\r\n\r\n").encode())
        data_received = ""
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received.strip())
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False


def remote_list():
    hasil = send_command("LIST")
    if hasil['status'] == 'OK':
        print("Daftar file:")
        for f in hasil['data']:
            print(f"- {f}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    hasil = send_command(f"GET {filename}")
    if hasil['status'] == 'OK':
        with open(hasil['data_namafile'], 'wb') as f:
            f.write(base64.b64decode(hasil['data_file']))
        print("File berhasil diunduh.")
        return True
    else:
        print("Gagal")
        return False

def remote_upload(local_filename, server_filename):
    try:
        with open(local_filename, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        hasil = send_command(f"UPLOAD {server_filename} {encoded}")
        print(hasil['data'])
        return hasil['status'] == 'OK'
    except Exception as e:
        print(f"Upload gagal: {e}")
        return False

def remote_delete(filename):
    hasil = send_command(f"DELETE {filename}")
    print(hasil['data'])
    return hasil['status'] == 'OK'

if __name__ == '__main__':
    while True:
        print("\nPilih perintah berikut:")
        print("1. LIST")
        print("2. GET <file>")
        print("3. UPLOAD <file>")
        print("4. DELETE <file>")
        print("5. Keluar")
        pilihan = input("Masukkan pilihan: ").strip()

        if pilihan == '1':
            remote_list()
        elif pilihan == '2':
            nama_file = input("Nama file yang akan diambil: ")
            remote_get(nama_file)
        elif pilihan == '3':
            lokal_file = input("Nama file lokal yang akan diupload: ")
            server_file = input("Nama file yang disimpan di server: ")
            remote_upload(lokal_file, server_file)
        elif pilihan == '4':
            nama_file = input("Nama file yang akan dihapus dari server: ")
            remote_delete(nama_file)
        elif pilihan == '5':
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid.")
