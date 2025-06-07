#!/usr/bin/env python3
import os
import base64
import logging
import socket
import json
from concurrent.futures import ProcessPoolExecutor

PORT = 6669
DATA_DIR = "server_temp"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
DELIMITER = b"\r\n\r\n"


# --------- File Operations ---------

def list_files():
    try:
        files = os.listdir(DATA_DIR)
        return {"status": "OK", "data": files}
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}


def read_file_base64(filename):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "rb") as f:
            content = f.read()
        return base64.b64encode(content).decode()
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")


def write_file_base64(filename, b64_content):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        content = base64.b64decode(b64_content)
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise RuntimeError(f"Error writing file: {e}")


# --------- Command Handlers ---------

def handle_list():
    return list_files()


def handle_get(params):
    if not params:
        return {"status": "ERROR", "data": "Missing filename parameter"}
    filename = params[0]
    try:
        data = read_file_base64(filename)
        return {"status": "OK", "data": data}
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}


def handle_upload(params):
    if len(params) < 2:
        return {"status": "ERROR", "data": "Missing filename or data parameter"}
    filename, b64_data = params[0], params[1]
    try:
        write_file_base64(filename, b64_data)
        return {"status": "OK", "data": "Uploaded"}
    except Exception as e:
        return {"status": "ERROR", "data": str(e)}


def handle_unknown():
    return {"status": "ERROR", "data": "Unknown command"}


# --------- Request Processing ---------

def parse_request(raw_request):
    parts = raw_request.strip().split(" ", 2)
    cmd = parts[0].upper()

    if cmd == "LIST":
        return handle_list()
    elif cmd == "GET":
        params = parts[1:] if len(parts) > 1 else []
        return handle_get(params)
    elif cmd == "UPLOAD":
        params = parts[1:] if len(parts) > 1 else []
        return handle_upload(params)
    else:
        return handle_unknown()


def receive_request(conn):
    buf = b""
    while DELIMITER not in buf:
        chunk = conn.recv(2**20)
        if not chunk:
            break
        buf += chunk
    raw_request = buf.split(DELIMITER)[0].decode()
    return raw_request


def handle_connection(fd):
    conn = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    try:
        raw_request = receive_request(conn)
        response = parse_request(raw_request)
    except Exception as e:
        logging.exception("Error processing request")
        response = {"status": "ERROR", "data": str(e)}

    conn.sendall(json.dumps(response).encode() + DELIMITER)
    conn.close()
    os.close(fd)


# --------- Server Setup ---------

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen()

    logging.info(f"Server listening on port {PORT} with max workers {MAX_WORKERS}")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            conn, _ = server_socket.accept()
            fd = os.dup(conn.fileno())
            executor.submit(handle_connection, fd)
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
