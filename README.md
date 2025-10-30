# Data Compression & Transfer Tool (DAA Project)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)

A Python application for a Design and Analysis of Algorithms (DAA) project. This tool implements, compares, and demonstrates three fundamental data compression algorithms. It features a complete Tkinter GUI, a client-server model to simulate file transfer, and an analysis tab to compare algorithm performance side-by-side.

## Features

* **Easy-to-use GUI** built with Tkinter.
* Compress and Decompress files using three different methods.
* **Built-in Analysis Tab** to run all three algorithms on a single file and generate a comparison table.
* **Client-Server Simulation** to demonstrate the real-world application of sending compressed files over a network.
* Automatic output file naming to prevent confusion.

## Algorithms Implemented

1.  **Huffman Coding** (A **Greedy** Approach)
2.  **LZW (Lempel-Ziv-Welch)** (A **Dictionary-based** Approach)
3.  **Shannon-Fano** (A **Divide and Conquer** Approach)

## Screenshot
<img width="1919" height="1021" alt="image" src="https://github.com/user-attachments/assets/639cd5f4-0843-451b-a8f4-5b5f47387d51" />

## Requirements

* Python 3.x

No external libraries are needed. The project uses built-in Python modules like `tkinter`, `socket`, `pickle`, and `subprocess`.

## How to Use

1.  Clone the repository:
    ```bash
    git clone [https://github.com/parth-g04/DATA_COMPRESSION_DAA.git](https://github.com/parth-g04/DATA_COMPRESSION_DAA.git)
    ```
2.  Navigate to the project directory:
    ```bash
    cd DATA_COMPRESSION_DAA
    ```
3.  Run the main GUI application:
    ```bash
    python gui.py
    ```

### Using the Tool

The GUI is organized into three tabs:

* **Tab 1: Compress / Decompress**
    * Select a single input file.
    * Choose a mode (Compress or Decompress).
    * Choose an algorithm.
    * The output filename is automatically generated for you.
    * Click "RUN TASK" to execute.

* **Tab 2: Client-Server Transfer**
    * Click "Start Server" to run the server in the background.
    * Enter the filename of a *compressed* file you want to transfer (e.g., `sample-huffman.bin`).
    * Click "Request File" to have the client connect to the server and download the file.
    * The file will be saved as `received_[filename]`.

* **Tab 3: Analysis & Comparison**
    * This is the best part of the project.
    * Click "Browse..." and select a large input file (like `sample.txt`).
    * Click **"RUN FULL ANALYSIS"**.
    * The tool will automatically compress your file using all three algorithms and display the results (original size, compressed size, and ratio) in the comparison table.

## Project File Structure
gui.py: The main Tkinter application that runs the project.

huffman.py: Implements the Huffman (Greedy) compression algorithm.

lzw.py: Implements the LZW (Dictionary-based) compression algorithm.

shannon_fano.py: Implements the Shannon-Fano (Divide & Conquer) algorithm.

server.py: The server script for the file transfer simulation.

client.py: The client script for the file transfer simulation.

sample.txt: A large sample text file (Alice in Wonderland) used for analysis.

README.md: This readme file.

## Author

* **Parth G. (parth-g04)**
