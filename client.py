import socket
import sys
HOST = '127.0.0.1'  
PORT = 9999         
BUFFER_SIZE = 4096  


if len(sys.argv) != 3:
    print("Usage: python client.py <filename_to_request> <filename_to_save_as>")
    print("Example: python client.py huffman_compressed.bin received_huffman.bin")
    sys.exit(1)

filename_to_request = sys.argv[1]
filename_to_save_as = sys.argv[2]


try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[+] Connecting to server at {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print("[+] Connected successfully.")

    print(f"[+] Requesting file: {filename_to_request}")
    client_socket.send(filename_to_request.encode())

   
    print(f"[+] Receiving data and saving to: {filename_to_save_as}")
    with open(filename_to_save_as, "wb") as f:
        while True:
           
            bytes_read = client_socket.recv(BUFFER_SIZE)
            
            if not bytes_read:
               
                break
                
        
            f.write(bytes_read)

    print(f"[+] File '{filename_to_save_as}' received successfully.")

except ConnectionRefusedError:
    print("[!] Connection refused. Is the server.py script running?")
except Exception as e:
    print(f"[!] An error occurred: {e}")

finally:

    client_socket.close()
    print("[+] Connection closed.")