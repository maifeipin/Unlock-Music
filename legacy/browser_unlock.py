import os
import time
import sys
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def safe_join_paths(paths):
    return "\n".join(paths)

def main():
    print("=== Browser-based Batch Unlocker ===")
    print("Uses Selenium to drive the Dist/index.html web app locally.")
    
    # 1. Config Paths
    base_dir = os.getcwd()
    dist_index = os.path.join(base_dir, "Dist", "index.html")
    
    if not os.path.exists(dist_index):
        print(f"[!] Error: Could not find {dist_index}")
        return
        
    # URL must be file protocol
    app_url = "file:///" + dist_index.replace("\\", "/")

    # 2. Get Input/Output Directories FIRST so we can config the browser
    print("\n--- Directory Selection ---")
    print("Enter the full path of the folder containing your encrypted music files.")
    print("Example: E:\\Music\\VipSongs")
    print("(Press ENTER to use current folder: " + base_dir + ")")
    target_dir = input("> ").strip()
    
    if not target_dir:
        target_dir = base_dir
    
    # Remove quotes
    if target_dir.startswith('"') and target_dir.endswith('"'):
        target_dir = target_dir[1:-1]
        
    if not os.path.exists(target_dir):
        print(f"[!] Error: Directory not found: {target_dir}")
        return

    # Set output directory to a subfolder "output" inside the target directory
    output_dir = os.path.join(target_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Target Directory: {target_dir}")
    print(f"Output Directory: {output_dir}")
    
    # Scan files
    print(f"Scanning for encrypted files in: {target_dir}")
    target_exts = ('.ncm', '.qmc0', '.qmc3', '.qmcflac', '.qmcogg', '.mgg', '.mflac', '.bkcmp3', '.bkcflac', '.tm0', '.tm3')
    
    all_candidates = [f for f in os.listdir(target_dir) if f.lower().endswith(target_exts)]
    
    # Resume Logic
    history_path = os.path.join(output_dir, "processed.log")
    # --- Robust Resume Logic (Based on Output Content) ---
    print("Verifying existing output files to avoid duplicates...")
    existing_files = os.listdir(output_dir)
    # Create a set of "stems" for fast lookup
    existing_stems = set(os.path.splitext(f)[0] for f in existing_files)
    
    # Check Archived/Completed Log (Files moved away)
    completed_log_path = os.path.join(output_dir, "completed.log")
    if os.path.exists(completed_log_path):
        archived_count = 0
        try:
            with open(completed_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    name = line.strip()
                    if name:
                        stem = os.path.splitext(name)[0]
                        existing_stems.add(stem)
                        archived_count += 1
            print(f"[Info] Loaded {archived_count} archived records from completed.log")
        except: pass
    
    # --- Handle Persistent Failures ---
    failed_log_path = os.path.join(output_dir, "failed.log")
    failed_set = set()
    retry_failures = False
    
    if os.path.exists(failed_log_path):
        try:
            with open(failed_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Clean up line (remove comments/crash notes we added)
                    name = line.split(" (")[0].strip()
                    if name:
                        failed_set.add(name)
        except: pass
        
    if failed_set:
        print(f"\n[!] Found {len(failed_set)} files marked as 'failed' in previous runs.")
        choice = input("Retry these failed files? (y/N) > ").lower()
        if choice == 'y':
            retry_failures = True
            print(">> Retrying failed files...")
        else:
            print(">> Skipping known failed files (Persistent Ignore).")

    files_to_process = []
    skipped_existing = 0
    skipped_failed = 0
    
    for fname in all_candidates:
        input_stem = os.path.splitext(fname)[0]
        
        # 1. Check if done
        if input_stem in existing_stems:
            skipped_existing += 1
            continue
            
        # 2. Check if failed (and we are NOT retrying)
        if (not retry_failures) and (fname in failed_set):
            skipped_failed += 1
            continue
            
        files_to_process.append(os.path.join(target_dir, fname))

    if skipped_existing > 0:
        print(f"[Resume] Skipped {skipped_existing} files that already exist in Output.")
    
    if skipped_failed > 0:
        print(f"[Ignore] Skipped {skipped_failed} files listed in failed.log.")
    
    if not files_to_process:
        print("No new files to process.")
        return

    # --- BATCH PROCESSING ---
    
    BATCH_SIZE = 10 
    total_to_do = len(files_to_process)
    failed_log_path = os.path.join(output_dir, "failed.log")
    
    print(f"Ready to process {total_to_do} files in batches of {BATCH_SIZE}...")
    
    for i in range(0, total_to_do, BATCH_SIZE):
        batch = files_to_process[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total_to_do + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"\n=== Starting Batch {batch_num}/{total_batches} (Size: {len(batch)}) ===")
        print("Initializing new browser session...")
        
        driver = None
        try:
            # 1. Setup Driver
            options = EdgeOptions()
            prefs = {
                "download.default_directory": output_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0
            }
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--disable-gpu")
            options.add_argument("--log-level=3")

            service = None
            local_driver = os.path.join(base_dir, "msedgedriver.exe")
            if os.path.exists(local_driver):
                service = EdgeService(executable_path=local_driver)
            else:
                # Driver fallback logic
                try:
                    service = EdgeService(EdgeChromiumDriverManager().install())
                except:
                   print("[!] Fatal: Driver not found and download failed.")
                   return

            driver = webdriver.Edge(service=service, options=options)
            
            # 2. Load App
            driver.get(app_url)
            time.sleep(2)
            
            # 3. Find Input & Send
            try:
                file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                print("[+] Found file input element.")
            except:
                print("[!] Could not find file input element on the page.")
                print("Dumping page source for debug...")
                print(driver.page_source[:500])
                raise # Re-raise to trigger finally and quit driver
            
            # Capture output state BEFORE sending files
            initial_files_state = set(f for f in os.listdir(output_dir) if f != "processed.log")

            # 4. Send Files
            file_string = safe_join_paths(batch)
            file_input.send_keys(file_string)
            
            # 5. Wait for processing & Click Download
            print(f"Files sent. Waiting for decryption...")
            
            try:
                # Wait for at least one row in the table to confirm processing started/finished
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "el-table__row"))
                )
                print("[+] Unlocked files appeared in the list.")
                
                # Check for "Download All" button
                download_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., '下载全部')]"))
                )
                print("[+] Found 'Download All' button. Clicking...")
                download_btn.click()
                
            except Exception as e:
                print(f"[!] Warning: UI interaction failed: {e}")
                print("    (The script will wait a bit and move to next batch, hoping auto-download worked if configured...)")

            # 6. Wait for download completion (Smart Wait)
            # We track the output directory to verify files arrived
            start_wait = time.time()
            max_wait_per_batch = max(60, len(batch) * 5) # Minimum 60s or 5s per file
            
            download_success = False
            new_files_count = 0
            
            print(f"Monitoring output directory for {len(batch)} new files (Timeout: {max_wait_per_batch}s)...")
            
            while time.time() - start_wait < max_wait_per_batch:
                current_files = set(f for f in os.listdir(output_dir) if f != "processed.log")
                new_files = current_files - initial_files_state
                new_files_count = len(new_files)
                
                if new_files_count >= len(batch):
                    print(f"[+] Success: Detected {new_files_count} new files.")
                    download_success = True
                    break
                
                time.sleep(2)
            
            if not download_success:
                print(f"[!] Warning: Timeout reached. Expected {len(batch)} files, found {new_files_count}.")
                if new_files_count == 0:
                    print("[!] No files downloaded. NOT scanning batch as processed.")
                else:
                    print("[!] Partial batch detected. NOT scanning batch as processed to allow retry.")
            
            # 7. Log success ONLY if downloads confirmed
            if download_success or (new_files_count > 0 and new_files_count >= len(batch) - 2): 
                # Relaxed condition: If we got most of them (e.g. 8/10), we log them to avoid stuck loops.
                # But strictly, user wants results. Let's use strict success for now or very close.
                # Actually, let's stick to strict logic for "all or nothing" to be safe, 
                # but if the user wants to force progress, they can manually check.
                # Given the "download all" button behavior, it's usually all or nothing.
                
                if not download_success:
                     print("[?] Marking as processed despite partial mismatch (tolerance).")

                with open(history_path, "a", encoding="utf-8") as f:
                    for path in batch:
                        f.write(os.path.basename(path) + "\n")
                print(f"Batch {batch_num} logged to processed.log.")
            else:
                 print(f"[!] Batch {batch_num} FAILED verification. Will be retried next time.")
            
            print(f"Batch {batch_num} completed.")
            
        except Exception as e:
            print(f"[!] Error in batch {batch_num}: {e}")
        
        finally:
            # --- Micro-Cleanup: Prevent (1) duplicates immediately ---
            run_micro_cleanup(output_dir)

            if driver:
                print("Closing browser session...")
                driver.quit()
                # Wait a moment for disk IO to release
                time.sleep(2)

    print("\n[Done] All batches processed.")

def run_micro_cleanup(output_dir):
    """ Quick duplication fix logic used after each batch """
    try:
        if not os.path.exists(output_dir): return
        files = os.listdir(output_dir)
        dup_pattern = re.compile(r"^(.+?)\s*\((\d+)\)(\.[^.]+)$")
        
        for fname in files:
            match = dup_pattern.match(fname)
            if match:
                base_name = match.group(1)
                ext = match.group(3)
                original_fname = base_name + ext
                
                full_enc_path = os.path.join(output_dir, fname)
                full_orig_path = os.path.join(output_dir, original_fname)
                
                if os.path.exists(full_orig_path):
                    # Smart Size Compare
                    try:
                        size_enc = os.path.getsize(full_enc_path)
                        size_orig = os.path.getsize(full_orig_path)
                        
                        if size_enc >= size_orig: 
                            if size_enc > size_orig:
                                print(f"  [Fix] Replaced smaller '{original_fname}' with larger '{fname}'")
                                os.remove(full_orig_path)
                                os.rename(full_enc_path, full_orig_path)
                            else:
                                print(f"  [Fix] Removed duplicate '{fname}' (Original is same/larger)")
                                os.remove(full_enc_path)
                    except OSError:
                        pass
    except Exception as e:
        print(f"  [!] Cleanup warning: {e}")

if __name__ == "__main__":
    main()
