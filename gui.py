import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import re # Added for parsing output
import threading # Added for running the server

class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DAA Project: Compression & Transfer Tool")
        self.root.geometry("800x650")
        
        # --- Class Variables ---
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.algorithm = tk.StringVar(value="huffman.py")
        self.mode = tk.StringVar(value="compress")
        self.server_process = None
        
        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), background="#0078d4", foreground="white")
        style.map("Accent.TButton", background=[('active', '#005a9e')])
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TRadiobutton", background="#f0f0f0")
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])
        
        # --- Main Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # --- Create Tabs ---
        self.tab_main = ttk.Frame(self.notebook, padding="10")
        self.tab_transfer = ttk.Frame(self.notebook, padding="10")
        self.tab_analysis = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.tab_main, text="Compress / Decompress")
        self.notebook.add(self.tab_transfer, text="Client-Server Transfer")
        self.notebook.add(self.tab_analysis, text="Analysis & Comparison")
        
        # --- Shared Output Console ---
        ttk.Label(main_frame, text="Output Console:", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 0))
        self.log_widget = scrolledtext.ScrolledText(main_frame, height=15, state="disabled", font=("Courier New", 9))
        self.log_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # --- Populate Tabs ---
        self.create_main_tab()
        self.create_transfer_tab()
        self.create_analysis_tab()
        
        # --- Bindings to auto-update filename ---
        self.input_file.trace_add("write", self.update_output_filename)
        self.algorithm.trace_add("write", self.update_output_filename)
        self.mode.trace_add("write", self.update_output_filename)

    def log(self, message):
        """Helper function to print to the GUI console."""
        self.log_widget.config(state="normal")
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.config(state="disabled")
        self.log_widget.see(tk.END) # Auto-scroll
        self.root.update_idletasks() # Force GUI update

    # --- TAB 1: Compress / Decompress ---
    
    def create_main_tab(self):
        frame = self.tab_main
        
        # Input
        in_frame = ttk.Frame(frame)
        in_frame.pack(fill=tk.X, pady=5)
        ttk.Label(in_frame, text="Input File:", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Entry(in_frame, textvariable=self.input_file, state="readonly", width=80).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(in_frame, text="Browse...", command=self.select_input).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(options_frame, text="Mode:", width=10).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Compress", variable=self.mode, value="compress").grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Decompress", variable=self.mode, value="decompress").grid(row=0, column=2, padx=5, sticky=tk.W)
        
        ttk.Label(options_frame, text="Algorithm:", width=10).grid(row=1, column=0, padx=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Huffman (Greedy)", variable=self.algorithm, value="huffman.py").grid(row=1, column=1, padx=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="LZW (Dictionary)", variable=self.algorithm, value="lzw.py").grid(row=1, column=2, padx=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="Shannon-Fano (D&C)", variable=self.algorithm, value="shannon_fano.py").grid(row=1, column=3, padx=5, sticky=tk.W)
        
        # Output (Automatic)
        out_frame = ttk.Frame(frame)
        out_frame.pack(fill=tk.X, pady=5)
        ttk.Label(out_frame, text="Output File:", width=10).pack(side=tk.LEFT, padx=5)
        self.output_file_label = ttk.Label(out_frame, text="(Select input file...)", style="TLabel", relief="sunken", padding=5, font=("Courier New", 10))
        self.output_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Run Button
        ttk.Button(frame, text="RUN TASK", style="Accent.TButton", command=self.run_process).pack(fill=tk.X, ipady=10, pady=20)

    def select_input(self):
        filename = filedialog.askopenfilename(title="Select Input File")
        if filename:
            self.input_file.set(filename)

    def update_output_filename(self, *args):
        """Auto-generates the output filename based on selections."""
        in_file = self.input_file.get()
        if not in_file:
            self.output_file_label.config(text="(Select input file...)")
            return

        algo_name = self.algorithm.get().split('.')[0]
        mode = self.mode.get()
        
        path, filename = os.path.split(in_file)
        basename, ext = os.path.splitext(filename)

        if mode == "compress":
            # Smartly handle re-compressing
            if "-huffman" in basename or "-lzw" in basename or "-shannon_fano" in basename:
                basename = basename.split('-')[0] # Get original name, e.g., "alice"
            
            out_filename = f"{basename}-{algo_name}.bin"
        else: # decompress
            # e.g., "alice-huffman.bin" -> "alice-huffman-decompressed.txt"
            out_filename = f"{basename}-decompressed.txt"
            
        full_out_path = os.path.join(path, out_filename)
        self.output_file.set(full_out_path)
        self.output_file_label.config(text=full_out_path)

    def run_process(self):
        """Runs the selected compression/decompression script."""
        script = self.algorithm.get()
        mode = self.mode.get()
        in_file = self.input_file.get()
        out_file = self.output_file.get()

        if not all([script, mode, in_file, out_file]):
            messagebox.showerror("Error", "Please select an input file.")
            return

        command = ['python', script, mode, in_file, out_file]
        self.log(f"Running command: {' '.join(command)}")
        self.log("-" * 30)
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            self.log(result.stdout)
            self.log("--- SUCCESS ---")
        except subprocess.CalledProcessError as e:
            self.log("--- ERROR ---")
            self.log(e.stderr)
        except FileNotFoundError:
            self.log(f"Error: Script '{script}' not found. Are all .py files in the same folder?")

    # --- TAB 2: Client-Server Transfer ---

    def create_transfer_tab(self):
        frame = self.tab_transfer
        
        # Server
        server_frame = ttk.LabelFrame(frame, text="Server Control", padding=10)
        server_frame.pack(fill=tk.X, pady=5)
        
        self.server_status_label = ttk.Label(server_frame, text="Server is: STOPPED", font=("Arial", 10, "bold"), foreground="red")
        self.server_status_label.pack(side=tk.LEFT, padx=10)
        self.start_server_btn = ttk.Button(server_frame, text="Start Server", command=self.start_server, width=20)
        self.start_server_btn.pack(side=tk.LEFT, padx=5)
        self.stop_server_btn = ttk.Button(server_frame, text="Stop Server", command=self.stop_server, width=20, state="disabled")
        self.stop_server_btn.pack(side=tk.LEFT, padx=5)
        
        # Client
        client_frame = ttk.LabelFrame(frame, text="Client Control", padding=10)
        client_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(client_frame, text="Filename to Request:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.file_to_request = ttk.Entry(client_frame, width=50)
        self.file_to_request.grid(row=0, column=1, padx=5, pady=5)
        self.file_to_request.insert(0, "huffman_alice.bin") # Example
        
        ttk.Button(client_frame, text="Request File", command=self.run_client, style="Accent.TButton").grid(row=0, column=2, padx=10, pady=5)

    def start_server(self):
        self.log("Starting server...")
        try:
            # Run server in a separate, non-blocking process
            self.server_process = subprocess.Popen(['python', '-u', 'server.py'], 
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                                    text=True, encoding='utf-8')
            self.server_status_label.config(text="Server is: RUNNING", foreground="green")
            self.start_server_btn.config(state="disabled")
            self.stop_server_btn.config(state="normal")
            self.log("Server is listening on 127.0.0.1:9999...")
            
            # Start a thread to read server output so it doesn't block
            threading.Thread(target=self.read_server_output, daemon=True).start()

        except Exception as e:
            self.log(f"Failed to start server: {e}")

    def read_server_output(self):
        # This function runs in a separate thread
        if self.server_process and self.server_process.stdout:
            for line in iter(self.server_process.stdout.readline, ''):
                self.log(f"[Server]: {line.strip()}")
            self.server_process.stdout.close()

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.log("Server stopped.")
            self.server_status_label.config(text="Server is: STOPPED", foreground="red")
            self.start_server_btn.config(state="normal")
            self.stop_server_btn.config(state="disabled")

    def run_client(self):
        filename = self.file_to_request.get()
        if not filename:
            messagebox.showerror("Error", "Please enter a filename to request.")
            return
            
        save_as = f"received_{filename}"
        command = ['python', 'client.py', filename, save_as]
        
        self.log(f"Running client: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            self.log(result.stdout)
            self.log(f"--- Client SUCCESS: File saved as {save_as} ---")
        except subprocess.CalledProcessError as e:
            self.log("--- Client ERROR ---")
            self.log(e.stdout)
            self.log(e.stderr)

    # --- TAB 3: Analysis & Comparison ---

    def create_analysis_tab(self):
        frame = self.tab_analysis
        
        # Input
        in_frame = ttk.Frame(frame)
        in_frame.pack(fill=tk.X, pady=5)
        ttk.Label(in_frame, text="File to Analyze:", width=15).pack(side=tk.LEFT, padx=5)
        self.analysis_file_entry = ttk.Entry(in_frame, state="readonly", width=80)
        self.analysis_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(in_frame, text="Browse...", command=self.select_analysis_file).pack(side=tk.LEFT, padx=5)
        
        # Run Button
        ttk.Button(frame, text="RUN FULL ANALYSIS", style="Accent.TButton", command=self.run_analysis).pack(fill=tk.X, ipady=10, pady=20)
        
        # Results Table
        ttk.Label(frame, text="Comparison Table", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))
        
        cols = ('Algorithm', 'Method', 'Original Size (bytes)', 'Compressed Size (bytes)', 'Ratio')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings', height=5)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def select_analysis_file(self):
        filename = filedialog.askopenfilename(title="Select File to Analyze")
        if filename:
            self.analysis_file_entry.config(state="normal")
            self.analysis_file_entry.delete(0, tk.END)
            self.analysis_file_entry.insert(0, filename)
            self.analysis_file_entry.config(state="readonly")

    def run_analysis(self):
        self.log("\n" + "="*30 + "\nStarting Full Analysis...\n" + "="*30)
        
        in_file = self.analysis_file_entry.get()
        if not in_file:
            messagebox.showerror("Error", "Please select a file to analyze.")
            return

        # Clear old table data
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        algorithms = [
            ("Huffman", "Greedy", "huffman.py"),
            ("LZW", "Dictionary", "lzw.py"),
            ("Shannon-Fano", "D&C", "shannon_fano.py")
        ]
        
        results = []
        for name, method, script in algorithms:
            self.log(f"--- Analyzing {name} ---")
            out_file = f"temp_analysis_{name}.bin"
            command = ['python', script, 'compress', in_file, out_file]
            
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
                self.log(result.stdout)
                
                # Parse the output
                parsed_data = self.parse_script_output(result.stdout)
                if parsed_data:
                    results.append((name, method, parsed_data['original'], parsed_data['compressed'], parsed_data['ratio']))
                else:
                    self.log(f"Could not parse output for {name}")

                # Clean up temp file
                if os.path.exists(out_file):
                    os.remove(out_file)
                    
            except Exception as e:
                self.log(f"Failed to run {name}: {e}")
        
        # Sort results by best ratio (highest)
        results.sort(key=lambda x: x[4], reverse=True)
        
        # Populate table
        for res in results:
            self.tree.insert("", tk.END, values=res)
            
        self.log("="*30 + "\nAnalysis Complete.\n" + "="*30)
        
    def parse_script_output(self, output):
        """Parses the console output from your scripts to find the data."""
        data = {}
        try:
            # Using regex to find the numbers
            org_match = re.search(r"Original file size: (\d+)", output)
            comp_match = re.search(r"Compressed file size: (\d+)", output)
            ratio_match = re.search(r"Compression Ratio: ([0-9.]+)", output)
            
            if org_match and comp_match and ratio_match:
                data['original'] = int(org_match.group(1))
                data['compressed'] = int(comp_match.group(1))
                data['ratio'] = float(ratio_match.group(1))
                return data
        except Exception as e:
            self.log(f"Parsing error: {e}")
            
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    # Make sure server is stopped when window is closed
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_server(), root.destroy()))
    root.mainloop()