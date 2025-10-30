import socket
import sys

# --- Configuration ---
HOST = '127.0.0.1'  # The server's IP address (localhost)
PORT = 9999         # The port used by the server
BUFFER_SIZE = 4096  # 4KB buffer for receiving data

# --- Get filename from command-line arguments ---
if len(sys.argv) != 3:
    print("Usage: python client.py <filename_to_request> <filename_to_save_as>")
    print("Example: python client.py huffman_compressed.bin received_huffman.bin")
    sys.exit(1)

filename_to_request = sys.argv[1]
filename_to_save_as = sys.argv[2]

# --- Create and connect the socket ---
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[+] Connecting to server at {HOST}:{PORT}...")
    client_socket.connect((HOST, PORT))
    print("[+] Connected successfully.")

    # --- Request and Receive the file ---
    
    # 1. Send the filename we want
    print(f"[+] Requesting file: {filename_to_request}")
    client_socket.send(filename_to_request.encode())

    # 2. Open a new file in write-binary ('wb') mode to save the data
    print(f"[+] Receiving data and saving to: {filename_to_save_as}")
    with open(filename_to_save_as, "wb") as f:
        while True:
            # Read data from the server
            bytes_read = client_socket.recv(BUFFER_SIZE)
            
            if not bytes_read:
                # If no more data is received, the file transfer is done
                break
                
            # Write the received bytes to the file
            f.write(bytes_read)

    print(f"[+] File '{filename_to_save_as}' received successfully.")

except ConnectionRefusedError:
    print("[!] Connection refused. Is the server.py script running?")
except Exception as e:
    print(f"[!] An error occurred: {e}")

finally:
    # Clean up the connection
    client_socket.close()
    print("[+] Connection closed.")