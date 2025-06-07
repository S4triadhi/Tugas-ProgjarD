#!/usr/bin/env python3
import socket
import json
import base64
import os

SERVER = ("127.0.0.1", 6669)
DELIMITER = "\r\n\r\n"

def send_command(command):
    """
    Sends a command to the server and returns the parsed JSON response.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(SERVER)
            s.sendall((command + DELIMITER).encode())

            buffer = ""
            while DELIMITER not in buffer:
                data = s.recv(4096)
                if not data:
                    break
                buffer += data.decode()

            # Cek jika response kosong
            if not buffer.strip():
                raise ValueError("Empty response from server")

            message = buffer.split(DELIMITER)[0]
            return json.loads(message)

    except json.JSONDecodeError as e:
        print("[ERROR] Failed to parse server response.")
        print("[DEBUG] Raw response:", repr(buffer))
        return {"status": "ERROR", "data": "Invalid JSON response"}
    except Exception as e:
        print(f"[ERROR] Failed to send command: {e}")
        return {"status": "ERROR", "data": str(e)}


def list_files():
    """
    Requests a list of files from the server.
    """
    response = send_command("LIST")
    if response.get("status") == "OK":
        return response.get("data", [])
    print("[ERROR] Failed to list files.")
    return []

def download_file(filename, save_as=None):
    """
    Downloads a file from the server and saves it locally.
    """
    response = send_command(f"GET {filename}")
    if response.get("status") == "OK":
        try:
            data = base64.b64decode(response["data"])
            save_name = save_as or f"dl_{filename}"
            with open(save_name, "wb") as f:
                f.write(data)
            print(f"[INFO] Downloaded {filename} -> {save_name} ({len(data)} bytes)")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save file: {e}")
    else:
        print(f"[ERROR] Server error: {response.get('data')}")
    return False

def upload_file(filepath):
    """
    Uploads a local file to the server.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File does not exist: {filepath}")
        return False

    try:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        filename = os.path.basename(filepath)
        response = send_command(f"UPLOAD {filename} {encoded}")
        if response.get("status") == "OK":
            print(f"[INFO] Uploaded {filename} successfully.")
            return True
        else:
            print(f"[ERROR] Upload failed: {response.get('data')}")
    except Exception as e:
        print(f"[ERROR] Failed to read or send file: {e}")
    return False
