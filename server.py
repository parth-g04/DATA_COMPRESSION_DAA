import socket
import os

# --- Configuration ---
HOST = '127.0.0.1'  # Standard loopback interface (localhost)
PORT = 9999         # Port to listen on
BUFFER_SIZE = 4096  # 4KB buffer for sending data

# --- Create and set up the socket ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

# Start listening for incoming connections
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}...")
print("Waiting for a client to connect...")

# --- Wait for a connection ---
# This line will block (wait) until a client connects
client_socket, client_address = server_socket.accept()
print(f"[+] Accepted connection from {client_address[0]}:{client_address[1]}")

try:
    # 1. Receive the filename request from the client
    filename_request = client_socket.recv(BUFFER_SIZE).decode()
    print(f"[+] Client is requesting file: {filename_request}")

    # 2. Check if the requested file exists
    if os.path.exists(filename_request):
        print(f"[+] File found. Sending '{filename_request}'...")
        
        # 3. Open the file in read-binary ('rb') mode
        with open(filename_request, "rb") as f:
            while True:
                # Read the file in chunks
                bytes_read = f.read(BUFFER_SIZE)
                
                if not bytes_read:
                    # If no more data is in the file, we are done
                    break
                    
                # Send the chunk of data to the client
                client_socket.sendall(bytes_read)
        
        print(f"[+] File sent successfully.")
        
    else:
        # 4. If file not found, send an error (or just close)
        print(f"[!] Error: File '{filename_request}' not found on server.")
        # We'll just close the connection, the client will see this.

except Exception as e:
    print(f"[!] An error occurred: {e}")

finally:
    # Clean up the connections
    client_socket.close()
    server_socket.close()
    print("[+] Connections closed.")