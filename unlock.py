import os
import subprocess
import sys

def main():
    print("=== Native Fast Unlocker (Powered by Go CLI) ===")
    print("This tool uses the compiled 'um.exe' for high-speed, stable decryption.")
    
    # Locate um.exe
    base_dir = os.path.dirname(os.path.abspath(__file__))
    um_path = os.path.join(base_dir, "cli", "um.exe")
    
    if not os.path.exists(um_path):
        print(f"[!] Error: 'um.exe' not found at: {um_path}")
        print("Please run the compilation step first or check path.")
        return

    # User Input
    print("\nEnter input directory containing encrypted files:")
    print(f"(Press ENTER to use current: {base_dir})")
    input_dir = input("> ").strip()
    if not input_dir: input_dir = base_dir
    if input_dir.startswith('"') and input_dir.endswith('"'): input_dir = input_dir[1:-1]
    
    output_dir = os.path.join(input_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Scan for valid encrypted files
    print(f"\nScanning: {input_dir}")
    target_exts = ('.ncm', '.qmc0', '.qmc3', '.qmcflac', '.qmcogg', '.mgg', '.mflac', 
                   '.bkcmp3', '.bkcflac', '.tm0', '.tm3', '.kwm', '.kgm')
    
    files_to_process = [f for f in os.listdir(input_dir) if f.lower().endswith(target_exts)]
    
    if not files_to_process:
        print("No supported encrypted files found.")
        print(f"Supported extensions: {target_exts}")
        return

    print(f"Found {len(files_to_process)} encrypted files. Starting fast unlock...\n")
    print(f"Output Directory: {output_dir}\n")

    success_count = 0
    fail_count = 0
    
    for idx, fname in enumerate(files_to_process, 1):
        full_path = os.path.join(input_dir, fname)
        
        # Print progress
        print(f"[{idx}/{len(files_to_process)}] Unlocking: {fname} ...", end="", flush=True)
        
        cmd = [um_path, "-i", full_path, "-o", output_dir]
        
        try:
            # Run per file. Keep it quiet unless verbose needed.
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print(" [OK]")
                success_count += 1
            else:
                print(" [FAILED]")
                print(f"    Error: {result.stderr.strip()}")
                fail_count += 1
                
        except Exception as e:
            print(f" [Error: {e}]")
            fail_count += 1

    print("\n" + "="*30)
    print("SUMMARY")
    print("="*30)
    print(f"Total Processed: {len(files_to_process)}")
    print(f"Success:         {success_count}")
    print(f"Failed:          {fail_count}")
    
    if fail_count > 0:
        print("\nNote: Failures might be due to unsupported formats or corrupted files.")
        
    print("\n[Done] Task completed.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
