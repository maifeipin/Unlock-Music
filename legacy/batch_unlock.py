import os
import time
import sys
from ncmdump import dump 


import os
import subprocess
import shutil

# NOTE: Since pure Python libraries for QMC/MGG (like QQMusicDecrypt) often require compilation environments
# or fail to build on Windows, the most reliable method is to use the binary 'unlock-music-cli'.
# 
# Please download 'unlock-music-cli' (e.g. from GitHub releases) and place 'um-cli.exe' or 'unlock-music-cli.exe'
# in this folder or your system PATH.

POSSIBLE_CLI_NAMES = ["um-cli.exe", "unlock-music-cli.exe", "unlock-music.exe"]

def find_cli_tool():
    # Check current dir
    for name in POSSIBLE_CLI_NAMES:
        if os.path.exists(name):
            return os.path.abspath(name)
    # Check PATH
    for name in POSSIBLE_CLI_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None

def unlock_directory(input_dir):
    cli_path = find_cli_tool()
    
    if not cli_path:
        print("\n[!] Error: 'unlock-music-cli' tool not found.")
        print("To unlock QMC/MGG/TM/NCM files reliably, please:")
        print("1. Download the CLI tool from: https://github.com/unlock-music/cli/releases")
        print("2. Rename it to 'um-cli.exe' and put it in this folder.")
        print("   (Or ensure it's in your system PATH)")
        return

    print(f"Using unlock tool: {cli_path}")
    print(f"Scanning directory: {input_dir}")
    
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a directory.")
        return

    # Extensions common for encrypted music
    target_exts = ('.ncm', '.qmc0', '.qmc3', '.qmcflac', '.qmcogg', '.mgg', '.mflac', '.bkcmp3', '.bkcflac', '.tm0', '.tm3')
    
    files_to_unlock = [f for f in os.listdir(input_dir) if f.lower().endswith(target_exts)]
    
    if not files_to_unlock:
        print("No supported encrypted files found.")
        return

    print(f"Found {len(files_to_unlock)} encrypted files. Starting batch unlock...")
    
    for filename in files_to_unlock:
        file_path = os.path.join(input_dir, filename)
        print(f"Processing: {filename} ...", end=" ")
        
        # Call the CLI tool
        # Usage usually: um-cli -i <input_file> -o <output_dir>
        # Or just um-cli <input_file> (check specific tool help)
        # We assume standard unlock-music-cli behavior
        
        try:
            # -i input, -o output. using '.' as output dir
            cmd = [cli_path, "-i", file_path, "-o", input_dir]
            
            # Run hidden to keep output clean, valid for some CLIs
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print("[OK]")
            else:
                print(f"[FAILED]")
                print(f"  > Output: {result.stdout}")
                print(f"  > Error: {result.stderr}")
                
        except Exception as e:
            print(f"[ERR] Execution failed: {e}")

    print("\nBatch processing complete.")

def main():
    print("=== Universal Batch Music Unlocker (Wrapper) ===")
    print("Supports: NCM, QMC, MGG, TM, etc. (via unlock-music-cli)")
    
    print("\nEnter the directory path containing encrypted files:")
    print("(Press Enter to scan current folder: " + os.getcwd() + ")")
    target_dir = input("> ").strip()
    
    if not target_dir:
        target_dir = os.getcwd()
        
    if target_dir.startswith('"') and target_dir.endswith('"'):
        target_dir = target_dir[1:-1]
        
    unlock_directory(target_dir)
    print("\nPress Enter to exit.")
    input()

if __name__ == "__main__":
    main()
