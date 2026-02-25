import socket
from threading import Thread
import os

class Client:

    def __init__(self, host, port):
        self.socket = socket.socket()
        self.socket.connect((host, port))
        self.name = input("Enter your name: ")
        self.talk_to_server()


    def talk_to_server(self):
        self.socket.send(self.name.encode())
        Thread(target=self.receive_messages).start()
        print("connection successful, type 'bye' to exit:")
        self.send_message()

    def send_message(self):
        while True:
            client_input = input(f"{self.name}: ")
            client_message = self.name + ": " + client_input
            self.socket.send(client_message.encode())
            if client_input.strip().lower() == "bye":
                break

    def receive_messages(self):
        while True:
            server_message = self.socket.recv(1024).decode()
            if not server_message.strip():
                os._exit(0)
            print("\033[1;31;40m" + server_message + "\033[0m")


if __name__ == "__main__":
    print("=== Chat Client ===")
    HOST = input("Enter server IP or Load Balancer DNS: ").strip()
    if not HOST:
        print("No address provided. Using localhost for testing.")
        HOST = 'localhost'
    PORT = 12345
    print(f"Connecting to {HOST}:{PORT}...")
    Client(HOST, PORT)