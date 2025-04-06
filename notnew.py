import os
import argparse
from pathlib import Path


class FileSplitterMerger:
    """Class to handle splitting and merging of files."""
    
    def __init__(self, chunk_size_mb=10):
        """Initialize with chunk size in MB."""
        self.chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
        
    def split_file(self, input_file, output_dir=None):
        """
        Split a file into chunks.
        
        Args:
            input_file (str): Path to the file to split
            output_dir (str, optional): Directory to save chunks. Defaults to input file directory.
            
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
                
        # Create a manifest file with metadata
        manifest_path = os.path.join(output_dir, f"{base_name}.manifest")
        with open(manifest_path, 'w') as manifest:
            manifest.write(f"original_file: {base_name}\n")
            manifest.write(f"total_chunks: {chunk_num}\n")
            manifest.write(f"chunk_size_bytes: {self.chunk_size}\n")
            
        print(f"Split complete: Created {chunk_num} chunks and a manifest file in {output_dir}")
        return chunk_files
    
    def merge_files(self, manifest_file, output_file=None):
        """
        Merge chunks back into the original file.
        
        Args:
            manifest_file (str): Path to the manifest file
            output_file (str, optional): Path for the merged output file
            
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
        
        # Merge all chunks
        with open(output_file, 'wb') as merged_file:
            for i in range(1, total_chunks + 1):
                chunk_path = os.path.join(manifest_path.parent, f"{original_filename}.part{i:03d}")
                
                if not os.path.exists(chunk_path):
                    raise FileNotFoundError(f"Chunk file missing: {chunk_path}")
                    
                with open(chunk_path, 'rb') as chunk:
                    merged_file.write(chunk.read())
                    
        print(f"Merge complete: File saved as {output_file}")
        return output_file


def main():
    """Command line interface for file splitter/merger."""
    parser = argparse.ArgumentParser(description="Split or merge files")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Split command
    split_parser = subparsers.add_parser('split', help='Split a file into chunks')
    split_parser.add_argument('input_file', help='File to split')
    split_parser.add_argument('-o', '--output-dir', help='Directory to save chunks')
    split_parser.add_argument('-s', '--chunk-size', type=int, default=10, 
                            help='Chunk size in MB (default: 10)')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge chunks back into a file')
    merge_parser.add_argument('manifest_file', help='Manifest file for the split')
    merge_parser.add_argument('-o', '--output-file', help='Path for the merged output file')
    
    args = parser.parse_args()
    
    if args.command == 'split':
        splitter = FileSplitterMerger(args.chunk_size)
        splitter.split_file(args.input_file, args.output_dir)
    elif args.command == 'merge':
        merger = FileSplitterMerger()
        merger.merge_files(args.manifest_file, args.output_file)
    else:
        parser.print_help()
        
        
if __name__ == "__main__":
    main()