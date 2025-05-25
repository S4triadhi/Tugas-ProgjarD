import socket
import json
import base64
import os
import logging

# Constants
SERVER_ADDRESS = ("172.16.16.101", 6669)
DELIMITER = "\r\n\r\n"
CHUNK_SIZE = 4096

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def send_command(command):
    """
    Sends a command string to the server and returns the parsed JSON response.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(SERVER_ADDRESS)
            logging.info(f"Connected to {SERVER_ADDRESS}")
            sock.sendall((command + DELIMITER).encode())

            buffer = ""
            while True:
                data = sock.recv(CHUNK_SIZE)
                if not data:
                    break
                buffer += data.decode()
                if DELIMITER in buffer:
                    break

            response_str = buffer.split(DELIMITER)[0]
            return json.loads(response_str)
    except Exception as e:
        logging.error(f"Connection or parsing error: {e}")
        return {"status": "ERROR", "data": str(e)}

def list_files():
    """
    Lists files available on the server.
    """
    response = send_command("LIST")
    if response.get("status") == "OK":
        print("File list on server:")
        for fname in response.get("data", []):
            print(f"- {fname}")
    else:
        print("Failed to list files.")

def download_file(filename):
    """
    Downloads a file from the server.
    """
    response = send_command(f"GET {filename}")
    if response.get("status") == "OK":
        content = base64.b64decode(response["data_file"])
        with open(response["data_namafile"], "wb") as f:
            f.write(content)
        print(f"Downloaded: {response['data_namafile']} ({len(content)} bytes)")
    else:
        print(f"Failed to download file: {filename}")

def upload_file(filepath):
    """
    Uploads a file to the server.
    """
    if not os.path.exists(filepath):
        print(f"File does not exist: {filepath}")
        return

    try:
        with open(filepath, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        filename = os.path.basename(filepath)
        command = f"UPLOAD {filename} {content}"
        response = send_command(command)

        if response.get("status") == "OK":
            print(f"Uploaded file: {filename}")
        else:
            print(f"Upload failed: {response.get('data')}")
    except Exception as e:
        print(f"Error during upload: {e}")

def delete_file(filename):
    """
    Sends a delete command for the specified file.
    """
    response = send_command(f"DELETE {filename}")
    if response.get("status") == "OK":
        print(f"Deleted file: {filename}")
    else:
        print(f"Failed to delete file: {filename}")

def main():
    while True:
        print("\nMenu:")
        print("1. LIST")
        print("2. GET <filename>")
        print("3. UPLOAD <filepath>")
        print("4. DELETE <filename>")
        print("5. EXIT")

        user_input = input("Enter command: ").strip()
        parts = user_input.split(maxsplit=1)

        match parts:
            case ["1"]:
                list_files()
            case ["2", filename]:
                download_file(filename.strip())
            case ["3", filepath]:
                upload_file(filepath.strip())
            case ["4", filename]:
                delete_file(filename.strip())
            case ["5"]:
                print("Exiting...")
                break
            case _:
                print("Invalid input.")

if __name__ == "__main__":
    main()
