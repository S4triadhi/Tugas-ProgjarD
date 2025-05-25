#!/usr/bin/env python3
import os
import base64
import json
import socket
import logging
from concurrent.futures import ThreadPoolExecutor

# === Configuration ===
PORT = 6669
DATA_DIR = "server_temp"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
DELIMITER = b"\r\n\r\n"

# === Ensure directory exists ===
os.makedirs(DATA_DIR, exist_ok=True)

def handle_client(conn):
    try:
        buf = b""
        while DELIMITER not in buf:
            chunk = conn.recv(1024 * 1024)  # 1 MB buffer
            if not chunk:
                break
            buf += chunk

        raw_request = buf.split(DELIMITER)[0].decode()
        parts = raw_request.strip().split(" ", 2)
        command = parts[0]

        if command == "LIST":
            files = os.listdir(DATA_DIR)
            response = {"status": "OK", "data": files}

        elif command == "UPLOAD":
            if len(parts) < 3:
                raise ValueError("UPLOAD requires filename and base64 data")
            filename, encoded_data = parts[1], parts[2]
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(encoded_data))
            response = {"status": "OK", "data": "Uploaded"}

        elif command == "GET":
            if len(parts) < 2:
                raise ValueError("GET requires filename")
            filename = parts[1]
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "rb") as f:
                encoded_data = base64.b64encode(f.read()).decode()
            response = {"status": "OK", "data": encoded_data}

        else:
            response = {"status": "ERROR", "data": "Unknown command"}

    except Exception as e:
        logging.exception("Error while handling request")
        response = {"status": "ERROR", "data": str(e)}

    # Send response
    conn.sendall(json.dumps(response).encode() + DELIMITER)
    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", PORT))
        server.listen()
        logging.info(f"[THREAD] Server running on port {PORT} with {MAX_WORKERS} workers")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            while True:
                conn, addr = server.accept()
                logging.info(f"Accepted connection from {addr}")
                pool.submit(handle_client, conn)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()
