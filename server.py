import socket
import os

HOST = '127.0.0.1' 
PORT = 9999        
BUFFER_SIZE = 4096 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}...")
print("Waiting for a client to connect...")

client_socket, client_address = server_socket.accept()
print(f"[+] Accepted connection from {client_address[0]}:{client_address[1]}")

try:
   
    filename_request = client_socket.recv(BUFFER_SIZE).decode()
    print(f"[+] Client is requesting file: {filename_request}")


    if os.path.exists(filename_request):
        print(f"[+] File found. Sending '{filename_request}'...")
        

        with open(filename_request, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                
                if not bytes_read:
                    break
                    
                client_socket.sendall(bytes_read)
        
        print(f"[+] File sent successfully.")
        
    else:
        print(f"[!] Error: File '{filename_request}' not found on server.")

except Exception as e:
    print(f"[!] An error occurred: {e}")

finally:
    client_socket.close()
    server_socket.close()
    print("[+] Connections closed.")