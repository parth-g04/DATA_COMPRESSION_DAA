import json
import sys 
import os   
import pickle 


def get_frequencies(text):
    """Counts the frequency of each character in the text."""
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    sorted_freq = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
    return sorted_freq

def find_split_point(sorted_freq):
    """Finds the best point to split the list into two "equal" frequency groups."""
    total_frequency = sum(item[1] for item in sorted_freq)
    current_sum = 0
    best_split_index = 0
    min_difference = float('inf')

    for i in range(len(sorted_freq) - 1):
        current_sum += sorted_freq[i][1]
        remaining_sum = total_frequency - current_sum
        difference = abs(current_sum - remaining_sum)
        if difference < min_difference:
            min_difference = difference
            best_split_index = i
        else:
            break
    return best_split_index + 1

def build_shannon_fano_codes(sorted_freq, current_code=""):
    """Recursively builds the Shannon-Fano codes (Divide and Conquer)."""
    codes = {}
    if len(sorted_freq) == 0:
        return {}
    if len(sorted_freq) == 1:
        char, freq = sorted_freq[0]
        codes[char] = current_code
        return codes

    split_point = find_split_point(sorted_freq)
    group_one = sorted_freq[:split_point]
    group_two = sorted_freq[split_point:]

    codes.update(build_shannon_fano_codes(group_one, current_code + "0"))
    codes.update(build_shannon_fano_codes(group_two, current_code + "1"))

    return codes

def compress(text):
    """Main function to compress text using Shannon-Fano."""
    if not text:
        return "", {}
    sorted_freq = get_frequencies(text)
    shannon_fano_codes = build_shannon_fano_codes(sorted_freq)
    encoded_text = ""
    for char in text:
        encoded_text += shannon_fano_codes[char]
    return encoded_text, shannon_fano_codes


def shannon_fano_decompress(encoded_text, codes_table):
    """Decompresses a string using the Shannon-Fano codes table."""
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


def pack_bits(encoded_text):
    """Packs a string of '0's and '1's into bytes."""
    padding_amount = (8 - len(encoded_text) % 8) % 8
    padded_encoded_text = encoded_text + ('0' * padding_amount)
    
    byte_list = []
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        byte_list.append(int(byte, 2))
        
    return bytearray(byte_list), padding_amount

def unpack_bits(byte_array, padding_amount):
    encoded_text_padded = ""
    for byte in byte_array:
        encoded_text_padded += bin(byte)[2:].zfill(8)
    encoded_text = encoded_text_padded[:len(encoded_text_padded) - padding_amount]
    return encoded_text



def compress_file(input_file, output_file):
    """Reads a file, compresses it, and saves it to a new file."""
    print(f"--- Compressing {input_file} with Shannon-Fano ---")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
        
    if not text:
        print("Error: Input file is empty.")
        return


    encoded_text, codes_table = compress(text)
    
    # Pack the bit string into bytes
    byte_array, padding = pack_bits(encoded_text)
    
    data_to_save = {
        'codes': codes_table,
        'padding': padding,
        'data': byte_array
    }
    
    # 4. Save the package to the output file using pickle
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
    print(f"--- Decompressing {input_file} with Shannon-Fano ---")

    # 1. Load the "package" from the compressed file
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
    
    # 3. Decompress the bit string (using the new function)
    decoded_text = shannon_fano_decompress(encoded_text, codes_table)
    
    # 4. Save the decompressed text to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
        
    print(f"Successfully decompressed and saved to {output_file}")



if __name__ == "__main__":
    
 
    
    if len(sys.argv) != 4:
        print("Usage: python shannon_fano.py <mode> <input_file> <output_file>")
        print("Example (compress): python shannon_fano.py compress sample.txt shannon_compressed.bin")
        print("Example (decompress): python shannon_fano.py decompress shannon_compressed.bin decompressed.txt")
        sys.exit(1)
        
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