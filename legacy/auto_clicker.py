
import pyautogui
import time
import sys
import keyboard
import os
import pygetwindow as gw

def main():
    print("=== Auto Save-As Confirmer ===")
    print("Purpose: Automatically hit 'Save' on file dialogs.")
    print("Mode: Window Title Detection (Faster & More Reliable)")
    print("----------------------------------------------------")
    print("1. This script loops and looks for a window named '另存为' (or 'Save As').")
    print("2. When found, it brings it to front and presses 'Enter'.")
    print("3. It waits a moment before looking again.")
    print("\n[!] To Stop: Keep holding 'Q' or press Ctrl+C in this terminal.")
    
    # Target window titles to look for
    # Adjust this list if your save window has a different name
    TARGET_TITLES = ["另存为", "Save As", "Enter name of file to save to…"]
    
    print(f"\nLooking for windows: {TARGET_TITLES}")
    print("Press ENTER to start monitoring...")
    input()
    print("RUNNING... (Press 'Q' to quit)")

    processed_count = 0
    
    try:
        while True:
            # 1. Check Exit
            if keyboard.is_pressed('q'):
                print("\n[STOP] 'Q' pressed. Exiting...")
                break
            
            # 2. Search for windows
            target_window = None
            all_windows = gw.getAllTitles()
            
            for title in all_windows:
                for target in TARGET_TITLES:
                    if target in title:
                        # Exact match usually better for dialogs, or 'starts with'
                        # But 'in' is safer if there are extra chars.
                        # We verify it's likely a dialog (usually small size, but title is key)
                        # Let's verify exact-ish match to avoid false positives?
                        # Windows "Save As" is usually exactly "另存为"
                        if title == target:
                            try:
                                wins = gw.getWindowsWithTitle(title)
                                if wins:
                                    target_window = wins[0]
                            except:
                                pass
                        break
                if target_window:
                    break
            
            # 3. Handle Window
            if target_window:
                try:
                    if not target_window.isActive:
                        target_window.activate()
                        time.sleep(0.2) # Wait for focus
                    
                    if target_window.isActive:
                        print(f"[ACTION] Found '{target_window.title}'. Pressing Enter...")
                        keyboard.press_and_release('enter')
                        processed_count += 1
                        print(f"Total Saved: {processed_count}")
                        
                        # Wait for window to actually close/process
                        time.sleep(1.0) 
                    else:
                        print(f"[WARN] Could not activate window '{target_window.title}'")
                        
                except Exception as e:
                    print(f"[ERR] interacting with window: {e}")
            
            # 4. Idle wait
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped by Ctrl+C.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
