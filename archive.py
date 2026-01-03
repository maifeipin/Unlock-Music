import os
import shutil
import time

def load_log(path):
    s = set()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s.add(line.strip())
        except: pass
    return s

def append_log(path, new_items):
    try:
        with open(path, "a", encoding="utf-8") as f:
            for item in new_items:
                f.write(item + "\n")
    except Exception as e:
        print(f"[!] Error writing log {path}: {e}")

def main():
    print("=== Music Archive & Sync Tool ===")
    print("Moves processed files to a larger storage and tracks history.")
    
    # 1. Get Source Dir (Encrypted Files + Output folder)
    base_dir = os.getcwd()
    print("\nEnter Source Directory (containing encrypted files & 'output' folder):")
    print(f"(Press ENTER to use current: {base_dir})")
    source_dir = input("> ").strip()
    if not source_dir: source_dir = base_dir
    if source_dir.startswith('"') and source_dir.endswith('"'): source_dir = source_dir[1:-1]
    
    output_dir = os.path.join(source_dir, "output")
    if not os.path.exists(output_dir):
        print(f"[!] Error: 'output' folder not found in {source_dir}")
        return

    # 2. Get Destination Dir
    print("\nEnter Destination Directory (Large Storage / NAS):")
    print("Supports local paths (F:\\Music) or SMB/Network paths (\\\\192.168.1.100\\Public\\Music)")
    dest_dir = input("> ").strip()
    if not dest_dir:
        print("[!] Destination required.")
        return
    if dest_dir.startswith('"') and dest_dir.endswith('"'): dest_dir = dest_dir[1:-1]
    
    dest_originals = os.path.join(dest_dir, "Originals")
    dest_converted = os.path.join(dest_dir, "Converted")
    
    # Create dirs
    for d in [dest_originals, dest_converted]:
        if not os.path.exists(d):
            os.makedirs(d)
            
    print(f"\nSource: {source_dir}")
    print(f"Target: {dest_dir}")
    print("------------------------------------------------")

    # 3. Scan Output for converted files
    converted_files = [f for f in os.listdir(output_dir) if not f.endswith('.log')]
    
    # Map valid stems to output files
    # stem -> mp3_filename
    output_map = {os.path.splitext(f)[0]: f for f in converted_files}
    
    # Scan Source for encrypted files
    target_exts = ('.ncm', '.qmc0', '.qmc3', '.qmcflac', '.qmcogg', '.mgg', '.mflac', '.bkcmp3', '.bkcflac', '.tm0', '.tm3')
    encrypted_files = [f for f in os.listdir(source_dir) if f.lower().endswith(target_exts)]
    
    # Normalize stems for robust matching
    # 1. Lowercase
    # 2. Replace _ with space (common in some downloaders)
    # 3. Collapse multiple spaces
    def normalize(s):
        s = s.lower().replace('_', ' ')
        return ' '.join(s.split())

    # Map normalized stem -> encrypted filename
    enc_map = {}
    for f in encrypted_files:
        enc_map[normalize(os.path.splitext(f)[0])] = f

    moved_count = 0
    orphans = 0
    completed_items = []
    
    print(f"Found {len(converted_files)} converted files. Matching with {len(encrypted_files)} originals...")
    
    # Iterate over OUTPUT files to find their original source
    for out_file in converted_files:
        out_stem_norm = normalize(os.path.splitext(out_file)[0])
        
        if out_stem_norm in enc_map:
            # Match Found!
            enc_file = enc_map[out_stem_norm]
            
            src_enc_path = os.path.join(source_dir, enc_file)
            src_out_path = os.path.join(output_dir, out_file)
            
            dst_enc_path = os.path.join(dest_originals, enc_file)
            dst_out_path = os.path.join(dest_converted, out_file)
            
            if not os.path.exists(src_enc_path):
                print(f"[Skip] Source file missing: {enc_file}")
                continue

            try:
                # Move Original
                shutil.move(src_enc_path, dst_enc_path)
                
                # Move Converted
                if os.path.exists(dst_out_path):
                    os.remove(dst_out_path) # Overwrite
                shutil.move(src_out_path, dst_out_path)
                
                print(f"[Moved] {out_stem_norm}")
                completed_items.append(enc_file)
                moved_count += 1
                
            except Exception as e:
                print(f"[!] Failed moving {out_stem_norm}: {e}")
        else:
            orphans += 1

    # --- Orphan Handling ---
    if orphans > 0:
        print(f"\n[!] Warning: {orphans} converted files had no matching encrypted file in source.")
        print("This usually means the original file was renamed, deleted, or has a different name structure.")
        print("Examples of unmatched files:")
        
        shown = 0
        orphan_files = []
        for out_file in converted_files:
            out_stem_norm = normalize(os.path.splitext(out_file)[0])
            if out_stem_norm not in enc_map:
                orphan_files.append(out_file)
                if shown < 3:
                    print(f" - {out_file}")
                    shown += 1
        
        user_choice = input(f"Move these {orphans} orphan files to destination anyway? (y/N) > ").strip().lower()
        
        if user_choice == 'y':
            print("Moving orphans...")
            for f in orphan_files:
                src_path = os.path.join(output_dir, f)
                dst_path = os.path.join(dest_converted, f)
                try:
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.move(src_path, dst_path)
                    
                    # Log them using their own name since original is unknown
                    completed_items.append(f)
                    moved_count += 1
                except Exception as e:
                    print(f"[!] Failed moving orphan {f}: {e}")

    # 4. Update Logs
    if completed_items:
        print(f"\nUpdating history logs with {len(completed_items)} items...")
        
        # Log 1: Source/output/completed.log
        so_log = os.path.join(output_dir, "completed.log")
        append_log(so_log, completed_items)
        
        # Log 2: Dest/completed.log
        dest_log = os.path.join(dest_dir, "completed.log")
        append_log(dest_log, completed_items)
        
    print(f"\n=== Archive Complete ===")
    print(f"Total Moved: {moved_count} pairs/files to {dest_dir}")
    print("Sync logs updated.")

if __name__ == "__main__":
    main()
