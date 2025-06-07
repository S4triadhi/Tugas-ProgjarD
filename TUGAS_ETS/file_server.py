from socket import *
import socket
import threading
import logging
import time
import sys

# Import custom file protocol handler
from file_protocol import FileProtocol

# Instantiate the file protocol object
fp = FileProtocol()


# === THREAD TO HANDLE EACH CLIENT CONNECTION ===
class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        """
        Initializes a new thread to handle client connection.
        """
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        """
        Run the thread: handles client request by reading and responding to messages.
        """
        buffer = ""
        try:
            while True:
                # Receive data from client
                data = self.connection.recv(1024)
                if not data:
                    break  # No more data, close connection

                # Append received data to buffer
                buffer += data.decode()

                # Check if the message has complete delimiter "\r\n\r\n"
                while "\r\n\r\n" in buffer:
                    # Split buffer into command and remaining
                    command, buffer = buffer.split("\r\n\r\n", 1)

                    # Process the command using the FileProtocol handler
                    hasil = fp.proses_string(command)

                    # Send result back to client with delimiter
                    self.connection.sendall((hasil + "\r\n\r\n").encode())

        except Exception as e:
            logging.warning(f"Thread error: {str(e)}")
        finally:
            self.connection.close()


# === MAIN SERVER CLASS THAT ACCEPTS CONNECTIONS ===
class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        """
        Initializes the server with given IP address and port.
        """
        self.ipinfo = (ipaddress, port)
        self.the_clients = []  # List to track active client threads

        # Create TCP socket
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        threading.Thread.__init__(self)

    def run(self):
        """
        Run the server: binds socket, listens for incoming connections,
        and starts a new thread for each client.
        """
        logging.warning(f"Server running on {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)

        while True:
            # Accept incoming connection
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning(f"Connection from {self.client_address}")

            # Start a new thread to handle the client
            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)


# === ENTRY POINT ===
def main():
    """
    Entry point of the program. Starts the server thread.
    """
    svr = Server(ipaddress='0.0.0.0', port=6669)
    svr.start()


if __name__ == "__main__":
    # Configure logging level and start main function
    logging.basicConfig(level=logging.WARNING)
    main()
