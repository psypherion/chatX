import socket
import threading
import os

HOST = "0.0.0.0"
PORT = 8080

clients = {}

def handle_client(conn, addr):
    try:
        conn.sendall(b"Enter your name: ")
        name = conn.recv(1024).decode().strip()
        if not name:
            conn.sendall(b"Name cannot be empty. Disconnecting...\n")
            conn.close()
            return

        clients[conn] = name
        broadcast(f"{name} has joined the chat.\n", conn)

        while True:
            try:
                message = conn.recv(1024).decode().strip()
                if not message:
                    break
                else:
                    broadcast(f"{name}: {message}\n", conn, name)  # Prepend sender's name to messages
            except ConnectionResetError:
                break

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        if conn in clients:
            broadcast(f"{clients[conn]} has left the chat.\n", conn)
            del clients[conn]
        conn.close()

def broadcast(message, sender_conn, sender_name=None):
    for conn in clients:
        try:
            if conn == sender_conn:
                # Clear the line and show "me: message"
                conn.sendall(f"\033[F\033[Kme: {message[len(sender_name) + 2:]}".encode())  # \033[F moves cursor up, \033[K clears line
            else:
                conn.sendall(message.encode())
        except Exception as e:
            print(f"Error broadcasting message: {e}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            print(f"New connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
