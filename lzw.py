import sys  # Added for command-line arguments
import os   # Added for getting file sizes
import pickle # Added to save/load the compressed file
from io import StringIO # Moved from inside the function

# 2. Function for LZW Compression
# (This is UNCHANGED from your code)
def lzw_compress(text):
    """Compresses a string using the LZW dictionary-based algorithm."""
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    w = ""
    compressed_output = []
    for c in text:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            compressed_output.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
    if w:
        compressed_output.append(dictionary[w])
    return compressed_output

# 3. Function for LZW Decompression
# (This is UNCHANGED from your code)
def lzw_decompress(compressed_data):
    """Decompresses a list of LZW codes back into a string."""
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}
    result = StringIO()
    w = chr(compressed_data.pop(0))
    result.write(w)
    for k in compressed_data:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError(f"Bad compressed code: {k}")
        result.write(entry)
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    return result.getvalue()

# --- NEW SECTION: File Handling Functions ---

def compress_file(input_file, output_file):
    """Reads a file, compresses it, and saves the list of codes."""
    print(f"--- Compressing {input_file} with LZW ---")
    
    # Read text from the input file
    try:
        with open(input_file, 'r', encoding='ascii', errors='ignore') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
        
    if not text:
        print("Error: Input file is empty.")
        return

    # 1. Compress the text (using your original function)
    compressed_data_list = lzw_compress(text)
    
    # 2. Save the list of codes to the output file using pickle
    # We use 'wb' (write bytes) mode
    with open(output_file, 'wb') as f:
        pickle.dump(compressed_data_list, f)
        
    # --- Analysis ---
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    ratio = original_size / compressed_size
    
    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression Ratio: {ratio:.2f}x")
    print(f"Successfully compressed and saved to {output_file}")


def decompress_file(input_file, output_file):
    """Reads a compressed LZW file, decompresses it, and saves the text."""
    print(f"--- Decompressing {input_file} with LZW ---")

    # 1. Load the list of codes from the compressed file
    # We use 'rb' (read bytes) mode
    try:
        with open(input_file, 'rb') as f:
            compressed_data_list = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except pickle.UnpicklingError:
        print(f"Error: File '{input_file}' is not a valid compressed file.")
        return

    # 2. Decompress the list of codes (using your original function)
    decoded_text = lzw_decompress(compressed_data_list)
    
    # 3. Save the decompressed text to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
        
    print(f"Successfully decompressed and saved to {output_file}")


# --- MODIFIED: Main execution block ---
if __name__ == "__main__":
    
    # This block checks for command-line arguments
    
    if len(sys.argv) != 4:
        print("Usage: python lzw.py <mode> <input_file> <output_file>")
        print("Example (compress): python lzw.py compress sample.txt lzw_compressed.bin")
        print("Example (decompress): python lzw.py decompress lzw_compressed.bin decompressed.txt")
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