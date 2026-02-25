import socket
import threading
import redis

class ChatServer:
    def __init__(self, host="0.0.0.0", port=12345, redis_host="", redis_port=6379):
        self.host = host
        self.port = port
        self.clients = []

        # ---------------------------------
        # Connect to Redis (TLS enabled)
        # ---------------------------------
        print(f"Connecting to Redis at {redis_host}:{redis_port} ...")
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            ssl=True,
            ssl_cert_reqs=None,   # OK for ElastiCache lab use
            decode_responses=True
        )

        # Test connection (fail fast)
        try:
            self.redis.ping()
            print("Redis connection successful.")
        except Exception as e:
            print("ERROR: Could not connect to Redis:")
            print(e)
            raise SystemExit

        # ---------------------------------
        # Pub/Sub setup
        # ---------------------------------
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("chatroom")

        # Start background listener
        threading.Thread(target=self.redis_listener, daemon=True).start()

    # ============================================
    # Listen for messages published by ANY server
    # ============================================
    def redis_listener(self):
        print("Subscribed to Redis channel: chatroom")
        for message in self.pubsub.listen():
            if message["type"] == "message":
                text = message["data"]
                print(f"FROM REDIS >>> {text}")   # <---- Important debug line
                self.broadcast_to_local_clients(text)

    # Send message to all clients connected to THIS instance
    def broadcast_to_local_clients(self, text):
        for client in list(self.clients):
            try:
                client.send((text + "\n").encode())
            except:
                self.clients.remove(client)

    # Publish message so ALL EC2 instances see it
    def broadcast(self, sender, msg):
        text = f"{sender}: {msg}"
        self.redis.publish("chatroom", text)

    # Handle a single client connection
    def handle_client(self, client, addr):
        print(f"Client connected: {addr}")

        try:
            client.send("Welcome to the distributed chat!\n".encode())
        except:
            return

        while True:
            try:
                msg = client.recv(1024).decode().strip()

                # If no data, it's a load balancer health check or client disconnect
                if not msg:
                    break

                print(f"[{addr}] {msg}")
                self.broadcast(str(addr), msg)

            except:
                break

        print(f"Client disconnected: {addr}")
        try:
            self.clients.remove(client)
        except:
            pass
        client.close()

    # Start the TCP server
    def start(self):
        print(f"Starting server on {self.host}:{self.port} ...")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(100)

        print("Server is running and waiting for connections...")

        while True:
            client, addr = server_socket.accept()
            self.clients.append(client)
            threading.Thread(
                target=self.handle_client, args=(client, addr), daemon=True
            ).start()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    # Replace with your Redis endpoint
    REDIS_ENDPOINT = "Example.serverless.use2.cache.amazonaws.com"

    server = ChatServer(
        host="0.0.0.0",
        port=12345,
        redis_host=REDIS_ENDPOINT,
        redis_port=6379
    )

    server.start()
