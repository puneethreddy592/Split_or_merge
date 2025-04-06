# Split_or_merge

A Python application that allows you to **split** any file into smaller chunks and **merge** them back together. This is useful for breaking large files into manageable pieces for easier transfer, storage, or sharing.

## ✨ Features

- Split any file type (zip, 7z, rar, mp4, documents, images, etc.)
- Merge previously split chunks back into the original file
- User-friendly **GUI interface**
- Command-line interface (**CLI**) for automation and scripts
- Progress tracking for both splitting and merging
- Customizable chunk size
- Works with files of any size

## 📸 Screenshots
<img width="732" alt="Screenshot 2025-03-11 at 12 19 49 PM" src="https://github.com/puneethreddy592/Split_or_merge/blob/5d3ae96fffa30e95a5b7fcc5456c242d996b5c07/Screenshot%202025-04-06%20161950.png" />


## 🛠 Installation

### Option 1: Download the Executable (Windows)

1. Download `new.exe` from the [Releases](https://github.com/puneethreddy592/Split_or_merge/blob/5d3ae96fffa30e95a5b7fcc5456c242d996b5c07/new.exe) section
2. Run the executable — no installation required!

### Option 2: Run from Source

```bash
git clone https://github.com/puneethreddy592/Split_or_merge.git
cd Split_or_merge # pip install pathlib, tinkter
python new.py
```

## 🚀 Usage

### Using the GUI (`new.exe` or `new.py`)

#### 🔹 To Split a File:
1. Open the **"Split Files"** tab.
2. Click **Browse** to select the file you want to split.
3. Choose an output directory (or use the default).
4. Set your desired chunk size (in MB).
5. Click **Split File**.

📁 A `.manifest` file and chunk files like `filename.part001`, `filename.part002`, etc., will be created in the output folder.

#### 🔹 To Merge Files:
1. Open the **"Merge Files"** tab.
2. Click **Browse** to select the `.manifest` file.
3. Choose an output file location (or use the default).
4. Click **Merge Files**.

📦 The original file will be restored accurately.

---

### Using the Command-Line Interface (`notnew.py`)

#### 🔹 Split a File:
```bash
python notnew.py split large_video.mp4 --chunk-size 50
```
#### 🔹 Merge Files:
```bash
python notnew.py merge large_video.mp4.manifest
```

## 📥 Command-line Arguments
### Split Command
```bash
split input_file [-o OUTPUT_DIR] [-s CHUNK_SIZE]
```
- input_file: File to split (required).
- `-o`, `--output-dir`: Directory to save chunks (optional).
- `-s`, `--chunk-size`: Chunk size in MB (default: 10).
### Merge Command
```bash
merge manifest_file [-o OUTPUT_FILE]
```
- `manifest_file`: Manifest file for the split (required).
- `-o`, `--output-file`: Path for the merged output file (optional).

- A `.manifest` file is created containing metadata about the split.

### 🔹 Merging Process:
- The `.manifest` file is read to determine chunk details.
- Chunks are read sequentially and merged.
- The original file is reconstructed accurately.

---

## 📄 License

This project is licensed under the **MIT License**.  
Feel free to use and modify!

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to fork the repo and submit a Pull Request to suggest improvements or fixes.
