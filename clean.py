import os
import re

def clean_and_sync():
    print("=== Improved Cleanup & Deduplication Tool ===")
    print("Goal: Clean 'output' folder and sync logs, ensuring NO duplicates.")
    
    # 1. Ask for directory
    print("\nEnter source directory (where encrypted files are):")
    base_dir = os.getcwd()
    print(f"(Press ENTER to use current: {base_dir})")
    target_dir = input("> ").strip()
    
    if not target_dir:
        target_dir = base_dir
    if target_dir.startswith('"') and target_dir.endswith('"'):
        target_dir = target_dir[1:-1]
        
    output_dir = os.path.join(target_dir, "output")
    
    if not os.path.exists(output_dir):
        print(f"[!] Error: Output directory not found: {output_dir}")
        return

    print(f"\nScanning Output Directory: {output_dir}")
    print("SAFE MODE: Source files in parent directory are untouched.")
    
    # ================================
    # STEP 1: Aggressive Deduplication
    # ================================
    print("\n--- Scanning for Duplicates ---")
    files = os.listdir(output_dir)
    files.sort()
    
    # Regex for "Name (N).ext" allowing flexible spaces
    # Group 1: Name, Group 2: Number, Group 3: Extension
    dup_pattern = re.compile(r"^(.+?)\s*\((\d+)\)(\.[^.]+)$")
    
    to_delete = []
    to_rename = []
    warnings = []
    
    for fname in files:
        if fname.lower().endswith('.log'): continue
        
        match = dup_pattern.match(fname)
        if match:
            base_name = match.group(1)
            ext = match.group(3)
            original_fname = base_name + ext
            
            full_enc_path = os.path.join(output_dir, fname)      # The (1) file
            full_orig_path = os.path.join(output_dir, original_fname) # The normal file
            
            if os.path.exists(full_orig_path):
                # Both exist. Compare size.
                size_enc = os.path.getsize(full_enc_path)   # The (N) file
                size_orig = os.path.getsize(full_orig_path) # The original
                
                if size_enc == size_orig:
                    print(f"[MATCH] Exact duplicate found: '{fname}'. Queueing for delete.")
                    to_delete.append(full_enc_path)
                elif size_orig > size_enc:
                    # Original is bigger. Assuming (N) is the one missing metadata/incomplete.
                    print(f"[SMART FIX] Original '{original_fname}' is larger ({size_orig} > {size_enc}). Deleting smaller duplicate '{fname}'.")
                    to_delete.append(full_enc_path)
                else:
                    # Duplicate (N) is bigger. Original likely damaged or missing metadata.
                    print(f"[SMART FIX] Duplicate '{fname}' is larger ({size_enc} > {size_orig}). Replacing original.")
                    to_delete.append(full_orig_path) # Delete small original
                    to_rename.append((full_enc_path, full_orig_path)) # Rename big duplicate to original
            else:
                # Only (N) exists
                print(f"[ORPHAN] '{fname}' seems to be '{original_fname}'. Queueing rename.")
                to_rename.append((full_enc_path, full_orig_path))

    # --- Execute Phase ---
    print(f"\nSummary: {len(to_delete)} files to delete, {len(to_rename)} files to rename/restore.")
    
    # Execute Deletes
    for path in to_delete:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Deleted: {os.path.basename(path)}")
        except OSError as e:
            print(f"[Err] Deleting {os.path.basename(path)}: {e}")
            
    # Execute Renames
    for src, dst in to_rename:
        try:
            # Check if src still exists (it might have been deleted if logic failed, but shouldn't happen here)
            # Check if dst exists (if we deleted it above, it's gone, so we can rename src to dst)
            if os.path.exists(src) and not os.path.exists(dst):
                os.rename(src, dst)
                print(f"Renamed: {os.path.basename(src)} -> {os.path.basename(dst)}")
        except OSError as e:
            print(f"[Err] Rename failed: {e}")

    # ================================
    # STEP 2: Clean Temporary Files
    # ================================
    print("\n--- Step 2: Removing Temporary/Incomplete Files ---")
    # Scan for .tmp, .crdownload (Chrome/Edge), .opdownload (Opera)
    # or GUID-like files that are common artifacts of crashed browsers
    temp_exts = ('.tmp', '.crdownload', '.opdownload')
    
    deleted_temps = 0
    current_files = os.listdir(output_dir) # Refresh list
    
    for fname in current_files:
        if fname.lower().endswith(temp_exts):
            full_path = os.path.join(output_dir, fname)
            try:
                os.remove(full_path)
                # print(f"Deleted temp file: {fname}") # Optional verbose
                deleted_temps += 1
            except OSError as e:
                print(f"[Err] Failed to delete temp {fname}: {e}")
                
    if deleted_temps > 0:
        print(f"Removed {deleted_temps} temporary/incomplete files.")
    else:
        print("No temporary files found.")

    # ================================
    # STEP 3: Perfect Log Sync
    # ================================
    print("\n--- Step 3: Logs Synchronization ---")
    
    # Reload file list after changes
    current_files = os.listdir(output_dir)
    # Stems in output
    valid_stems = set(os.path.splitext(f)[0] for f in current_files if not f.endswith('.log'))
    
    # Map Source -> Output
    target_exts = ('.ncm', '.qmc0', '.qmc3', '.qmcflac', '.qmcogg', '.mgg', '.mflac', '.bkcmp3', '.bkcflac', '.tm0', '.tm3')
    source_files = [f for f in os.listdir(target_dir) if f.lower().endswith(target_exts)]
    
    processed_files = []
    
    # We rebuild processed.log to include ANY source file whose stem exists in output
    for src in source_files:
        src_stem = os.path.splitext(src)[0]
        if src_stem in valid_stems:
            processed_files.append(src)
            
    # Write processed.log
    with open(os.path.join(output_dir, "processed.log"), "w", encoding="utf-8") as f:
        for pf in processed_files:
            f.write(pf + "\n")
            
    print(f"Updated 'processed.log': {len(processed_files)} valid records.")
            
    # Clean failed.log
    failed_path = os.path.join(output_dir, "failed.log")
    if os.path.exists(failed_path):
        real_failures = []
        with open(failed_path, "r", encoding="utf-8") as f:
            for line in f:
                name = line.split(" (")[0].strip()
                if not name: continue
                # if stem is now in valid_stems, it succeeded!
                if os.path.splitext(name)[0] not in valid_stems:
                    real_failures.append(line.strip())
        
        with open(failed_path, "w", encoding="utf-8") as f:
            for rf in real_failures:
                f.write(rf + "\n")
        print(f"Updated 'failed.log': {len(real_failures)} remaining failures.")

    print("\n=== Done ===")
    print("Your Output directory should now be clean.")
    input("Press Enter to finish...")

if __name__ == "__main__":
    clean_and_sync()
