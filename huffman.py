import heapq
import os
import sys  # Added for command-line arguments
import pickle # Added to save the compressed file + code table

# 1. Define the Node class for the Huffman Tree
# (This is UNCHANGED from your code)
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# 2. Function to build the frequency table
# (This is UNCHANGED from your code)
def build_frequency_table(text):
    """Calculates the frequency of each character in the text."""
    freq_table = {}
    for char in text:
        if char not in freq_table:
            freq_table[char] = 0
        freq_table[char] += 1
    return freq_table

# 3. Function to build the Huffman Tree
# (This is UNCHANGED from your code)
def build_huffman_tree(freq_table):
    """Builds the Huffman Tree using a priority queue."""
    priority_queue = []
    
    for char, freq in freq_table.items():
        node = HuffmanNode(char, freq)
        heapq.heappush(priority_queue, node)

    while len(priority_queue) > 1:
        left_node = heapq.heappop(priority_queue)
        right_node = heapq.heappop(priority_queue)

        merged_node = HuffmanNode(None, left_node.freq + right_node.freq)
        merged_node.left = left_node
        merged_node.right = right_node

        heapq.heappush(priority_queue, merged_node)

    return priority_queue[0]

# 4. Function to generate the codes
# (This is UNCHANGED from your code)
def build_codes_table(tree_root):
    """Generates the Huffman codes by traversing the tree."""
    codes_table = {}

    def traverse_tree(current_node, current_code):
        if current_node.char is None:
            traverse_tree(current_node.left, current_code + "0")
            traverse_tree(current_node.right, current_code + "1")
        else:
            codes_table[current_node.char] = current_code

    traverse_tree(tree_root, "")
    return codes_table

# 5. Main function to compress text
# (This is UNCHANGED from your code)
def huffman_compress(text):
    """Compresses a given string using Huffman Coding."""
    if not text:
        return "", {}
    freq_table = build_frequency_table(text)
    huffman_tree_root = build_huffman_tree(freq_table)
    codes_table = build_codes_table(huffman_tree_root)
    encoded_text = ""
    for char in text:
        encoded_text += codes_table[char]
    return encoded_text, codes_table

# 6. Main function to decompress text
# (This is UNCHANGED from your code)
def huffman_decompress(encoded_text, codes_table):
    """Decompresses a string using the Huffman codes table."""
    if not encoded_text:
        return ""
    reversed_codes_table = {code: char for char, code in codes_table.items()}
    decoded_text = ""
    current_code = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in reversed_codes_table:
            char = reversed_codes_table[current_code]
            decoded_text += char
            current_code = ""
    return decoded_text

# --- NEW SECTION: Bit/Byte Packing Functions ---

def pack_bits(encoded_text):
    """Packs a string of '0's and '1's into bytes."""
    # Calculate padding
    # We need the text length to be a multiple of 8
    padding_amount = (8 - len(encoded_text) % 8) % 8
    padded_encoded_text = encoded_text + ('0' * padding_amount)
    
    # Convert padded text into a list of integers
    byte_list = []
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        byte_list.append(int(byte, 2))
        
    # Convert list of integers into a byte array
    return bytearray(byte_list), padding_amount

def unpack_bits(byte_array, padding_amount):
    """Unpacks bytes into a string of '0's and '1's."""
    encoded_text_padded = ""
    for byte in byte_array:
        # Convert each byte (int) to its 8-bit binary string
        encoded_text_padded += bin(byte)[2:].zfill(8)
        
    # Remove the padding
    encoded_text = encoded_text_padded[:len(encoded_text_padded) - padding_amount]
    return encoded_text

# --- NEW SECTION: File Handling Functions ---

def compress_file(input_file, output_file):
    """Reads a file, compresses it, and saves it to a new file."""
    print(f"--- Compressing {input_file} ---")
    
    # Read text from the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
        
    if not text:
        print("Error: Input file is empty.")
        return

    # 1. Compress the text (using your original function)
    encoded_text, codes_table = huffman_compress(text)
    
    # 2. Pack the bit string into bytes
    byte_array, padding = pack_bits(encoded_text)
    
    # 3. Create a "package" to save
    # This package contains everything needed for decompression
    data_to_save = {
        'codes': codes_table,
        'padding': padding,
        'data': byte_array
    }
    
    # 4. Save the package to the output file using pickle
    # We use 'wb' (write bytes) mode
    with open(output_file, 'wb') as f:
        pickle.dump(data_to_save, f)
        
    # --- Analysis ---
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    ratio = original_size / compressed_size
    
    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression Ratio: {ratio:.2f}x")
    print(f"Successfully compressed and saved to {output_file}")


def decompress_file(input_file, output_file):
    """Reads a compressed file, decompresses it, and saves the text."""
    print(f"--- Decompressing {input_file} ---")

    # 1. Load the "package" from the compressed file
    # We use 'rb' (read bytes) mode
    try:
        with open(input_file, 'rb') as f:
            loaded_data = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except pickle.UnpicklingError:
        print(f"Error: File '{input_file}' is not a valid compressed file.")
        return

    codes_table = loaded_data['codes']
    padding = loaded_data['padding']
    byte_array = loaded_data['data']

    # 2. Unpack the bytes back into the bit string
    encoded_text = unpack_bits(byte_array, padding)
    
    # 3. Decompress the bit string (using your original function)
    decoded_text = huffman_decompress(encoded_text, codes_table)
    
    # 4. Save the decompressed text to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
        
    print(f"Successfully decompressed and saved to {output_file}")


# --- MODIFIED: Main execution block ---
if __name__ == "__main__":
    
    # This block now checks for command-line arguments
    # sys.argv is a list of arguments.
    # sys.argv[0] is 'huffman.py'
    # sys.argv[1] is the mode ('compress' or 'decompress')
    # sys.argv[2] is the input_file
    # sys.argv[3] is the output_file
    
    if len(sys.argv) != 4:
        print("Usage: python huffman.py <mode> <input_file> <output_file>")
        print("Example (compress): python huffman.py compress sample.txt huffman_compressed.bin")
        print("Example (decompress): python huffman.py decompress huffman_compressed.bin decompressed.txt")
        sys.exit(1) # Exit the script
        
    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if mode == 'compress':
        compress_file(input_file, output_file)
    elif mode == 'decompress':
        decompress_file(input_file, output_file)
    else:
        print(f"Error: Invalid mode '{mode}'. Please use 'compress' or 'decompress'.")
        sys.exit(1)