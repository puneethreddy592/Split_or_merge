import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading


class FileSplitterMerger:
    """Class to handle splitting and merging of files."""
    
    def __init__(self, chunk_size_mb=10):
        """Initialize with chunk size in MB."""
        self.chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
        
    def split_file(self, input_file, output_dir=None, progress_callback=None):
        """
        Split a file into chunks.
        
        Args:
            input_file (str): Path to the file to split
            output_dir (str, optional): Directory to save chunks. Defaults to input file directory.
            progress_callback (function, optional): Function to call with progress updates
            
        Returns:
            list: List of created chunk files
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_file}")
            
        # Use input file directory if output_dir not specified
        if output_dir is None:
            output_dir = input_path.parent
        else:
            os.makedirs(output_dir, exist_ok=True)
            
        base_name = input_path.name
        chunk_files = []
        
        # Get total file size for progress reporting
        total_size = os.path.getsize(input_file)
        bytes_processed = 0
        
        with open(input_file, 'rb') as f:
            chunk_num = 0
            
            while True:
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                    
                chunk_num += 1
                chunk_filename = os.path.join(output_dir, f"{base_name}.part{chunk_num:03d}")
                with open(chunk_filename, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                    
                chunk_files.append(chunk_filename)
                
                # Update progress
                bytes_processed += len(chunk_data)
                if progress_callback:
                    progress = (bytes_processed / total_size) * 100
                    progress_callback(progress)
                
        # Create a manifest file with metadata
        manifest_path = os.path.join(output_dir, f"{base_name}.manifest")
        with open(manifest_path, 'w') as manifest:
            manifest.write(f"original_file: {base_name}\n")
            manifest.write(f"total_chunks: {chunk_num}\n")
            manifest.write(f"chunk_size_bytes: {self.chunk_size}\n")
            
        return chunk_files
    
    def merge_files(self, manifest_file, output_file=None, progress_callback=None):
        """
        Merge chunks back into the original file.
        
        Args:
            manifest_file (str): Path to the manifest file
            output_file (str, optional): Path for the merged output file
            progress_callback (function, optional): Function to call with progress updates
            
        Returns:
            str: Path to the merged file
        """
        manifest_path = Path(manifest_file)
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
            
        # Parse manifest file
        with open(manifest_file, 'r') as f:
            manifest_data = {}
            for line in f:
                key, value = line.strip().split(': ')
                manifest_data[key] = value
                
        original_filename = manifest_data['original_file']
        total_chunks = int(manifest_data['total_chunks'])
        
        # Determine output path
        if output_file is None:
            output_file = os.path.join(manifest_path.parent, f"merged_{original_filename}")
        
        # Calculate total size for progress reporting
        total_size = 0
        for i in range(1, total_chunks + 1):
            chunk_path = os.path.join(manifest_path.parent, f"{original_filename}.part{i:03d}")
            if os.path.exists(chunk_path):
                total_size += os.path.getsize(chunk_path)
                
        bytes_processed = 0
        
        # Merge all chunks
        with open(output_file, 'wb') as merged_file:
            for i in range(1, total_chunks + 1):
                chunk_path = os.path.join(manifest_path.parent, f"{original_filename}.part{i:03d}")
                
                if not os.path.exists(chunk_path):
                    raise FileNotFoundError(f"Chunk file missing: {chunk_path}")
                    
                with open(chunk_path, 'rb') as chunk:
                    chunk_data = chunk.read()
                    merged_file.write(chunk_data)
                    
                    # Update progress
                    bytes_processed += len(chunk_data)
                    if progress_callback:
                        progress = (bytes_processed / total_size) * 100
                        progress_callback(progress)
                    
        return output_file


class SplitMergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Splitter & Merger")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Set theme and style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Set colors
        bg_color = "#f0f0f0"
        btn_color = "#4a86e8"
        
        # Configure styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TButton', background=btn_color, foreground='white')
        self.style.configure('TLabel', background=bg_color)
        self.style.configure('TProgressbar', thickness=15)
        
        self.root.configure(bg=bg_color)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.split_tab = ttk.Frame(self.notebook)
        self.merge_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.split_tab, text="Split Files")
        self.notebook.add(self.merge_tab, text="Merge Files")
        
        # Set up split tab
        self.setup_split_tab()
        
        # Set up merge tab
        self.setup_merge_tab()
        
        # Initialize splitter/merger
        self.splitter_merger = FileSplitterMerger()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_split_tab(self):
        # File selection frame
        file_frame = ttk.Frame(self.split_tab)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.split_input_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.split_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.split_output_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.split_output_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_dir).grid(row=1, column=2)
        
        # Chunk size frame
        chunk_frame = ttk.Frame(self.split_tab)
        chunk_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(chunk_frame, text="Chunk Size (MB):").pack(side=tk.LEFT, padx=5)
        self.chunk_size_var = tk.IntVar(value=10)
        chunk_spin = ttk.Spinbox(chunk_frame, from_=1, to=1000, textvariable=self.chunk_size_var, width=5)
        chunk_spin.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(self.split_tab)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.split_progress_var = tk.DoubleVar()
        self.split_progress = ttk.Progressbar(progress_frame, variable=self.split_progress_var, maximum=100)
        self.split_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(self.split_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.split_button = ttk.Button(button_frame, text="Split File", command=self.start_split)
        self.split_button.pack(side=tk.RIGHT, padx=5)
        
    def setup_merge_tab(self):
        # File selection frame
        file_frame = ttk.Frame(self.merge_tab)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Manifest File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.merge_input_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.merge_input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_manifest_file).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.merge_output_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.merge_output_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_merge_output).grid(row=1, column=2)
        
        # Progress frame
        progress_frame = ttk.Frame(self.merge_tab)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.merge_progress_var = tk.DoubleVar()
        self.merge_progress = ttk.Progressbar(progress_frame, variable=self.merge_progress_var, maximum=100)
        self.merge_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(self.merge_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.merge_button = ttk.Button(button_frame, text="Merge Files", command=self.start_merge)
        self.merge_button.pack(side=tk.RIGHT, padx=5)
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(title="Select file to split")
        if filename:
            self.split_input_var.set(filename)
            # Default output directory to the same as input file
            self.split_output_var.set(os.path.dirname(filename))
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.split_output_var.set(directory)
    
    def browse_manifest_file(self):
        filename = filedialog.askopenfilename(title="Select manifest file", 
                                              filetypes=[("Manifest files", "*.manifest"), ("All files", "*.*")])
        if filename:
            self.merge_input_var.set(filename)
            
            # Try to set default output file based on manifest
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        if line.startswith("original_file:"):
                            original_name = line.strip().split(': ')[1]
                            output_path = os.path.join(os.path.dirname(filename), f"merged_{original_name}")
                            self.merge_output_var.set(output_path)
                            break
            except:
                pass
    
    def browse_merge_output(self):
        filename = filedialog.asksaveasfilename(title="Select output file")
        if filename:
            self.merge_output_var.set(filename)
    
    def update_split_progress(self, value):
        self.split_progress_var.set(value)
        self.root.update_idletasks()
    
    def update_merge_progress(self, value):
        self.merge_progress_var.set(value)
        self.root.update_idletasks()
    
    def start_split(self):
        input_file = self.split_input_var.get()
        output_dir = self.split_output_var.get()
        chunk_size = self.chunk_size_var.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
            
        if not output_dir:
            output_dir = os.path.dirname(input_file)
            
        # Update UI
        self.split_button.config(state=tk.DISABLED)
        self.status_var.set("Splitting file...")
        self.split_progress_var.set(0)
        
        # Create splitter with selected chunk size
        self.splitter_merger = FileSplitterMerger(chunk_size)
        
        # Run in separate thread to keep UI responsive
        def split_thread():
            try:
                self.splitter_merger.split_file(input_file, output_dir, self.update_split_progress)
                
                # Update UI after completion
                self.root.after(0, lambda: self.status_var.set("Split complete!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                           f"File split complete!\nOutput directory: {output_dir}"))
                self.root.after(0, lambda: self.split_button.config(state=tk.NORMAL))
                
            except Exception as e:
                # Handle errors
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.split_button.config(state=tk.NORMAL))
                
        threading.Thread(target=split_thread, daemon=True).start()
    
    def start_merge(self):
        manifest_file = self.merge_input_var.get()
        output_file = self.merge_output_var.get()
        
        if not manifest_file:
            messagebox.showerror("Error", "Please select a manifest file")
            return
            
        # Update UI
        self.merge_button.config(state=tk.DISABLED)
        self.status_var.set("Merging files...")
        self.merge_progress_var.set(0)
        
        # Run in separate thread to keep UI responsive
        def merge_thread():
            try:
                self.splitter_merger.merge_files(manifest_file, output_file, self.update_merge_progress)
                
                # Update UI after completion
                self.root.after(0, lambda: self.status_var.set("Merge complete!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                           f"Files merged successfully!\nOutput file: {output_file}"))
                self.root.after(0, lambda: self.merge_button.config(state=tk.NORMAL))
                
            except Exception as e:
                # Handle errors
                self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.merge_button.config(state=tk.NORMAL))
                
        threading.Thread(target=merge_thread, daemon=True).start()


def main():
    root = tk.Tk()
    app = SplitMergeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()