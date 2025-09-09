import os
import sys
import time
import threading
from pathlib import Path
import mimetypes

# Try to import pymediainfo gracefully
try:
    from pymediainfo import MediaInfo
    HAS_MEDIainfo = True
except ImportError:
    HAS_MEDIainfo = False
    print("⚠️ Warning: pymediainfo module not found. Media duration info will be skipped.\n")

# Format duration from seconds to HhMmSs format
def format_duration(seconds):
    seconds = int(seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60

    if hrs > 0:
        return f"{hrs}h{mins}m{secs}s"
    elif mins > 0:
        return f"{mins}m{secs}s"
    else:
        return f"{secs}s"

# Spinner for simple processing UI in CLI
class Spinner:
    spinner_cycle = ['|', '/', '-', '\\']

    def __init__(self):
        self.running = False
        self.thread = None

    def spinner_task(self):
        idx = 0
        while self.running:
            print(f"\rScanning... {self.spinner_cycle[idx % len(self.spinner_cycle)]}", end='', flush=True)
            idx += 1
            time.sleep(0.1)
        print('\r', end='')  # Clear line when done

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

def scan_directory(folder_path, output_file):
    folder = Path(folder_path)
    if not folder.is_dir():
        print("❌ Invalid directory.")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"📁 Directory Scan Report for: {folder_path}\n")
        f.write("=" * 50 + "\n\n")

        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = Path(root) / file
                mime_type, _ = mimetypes.guess_type(file_path)

                f.write(f"📝 File: {file}\n")
                f.write(f"    📂 Path: {file_path}\n")
                f.write(f"    🧾 Type: {mime_type}\n")

                # Media info extraction if possible and applicable
                if HAS_MEDIainfo and mime_type and ("video" in mime_type or "audio" in mime_type):
                    try:
                        media_info = MediaInfo.parse(file_path)
                        duration_found = False
                        for track in media_info.tracks:
                            if track.duration:
                                duration_sec = float(track.duration) / 1000
                                formatted_duration = format_duration(duration_sec)
                                f.write(f"    ⏱️ Duration: {formatted_duration}\n")
                                duration_found = True
                                break
                        if not duration_found:
                            f.write("    ⏱️ Duration: Not found\n")
                    except Exception as e:
                        f.write(f"    ⚠️ Could not extract media info: {e}\n")
                f.write("\n")

def main():
    target = input("📂 Enter path to scan: ").strip('"')
    output_file = Path(target) / "dir_info.txt"

    spinner = Spinner()
    spinner.start()

    try:
        scan_directory(target, output_file)
    finally:
        spinner.stop()

    print(f"\n✅ Scan complete! Results saved in '{output_file}'")

if __name__ == "__main__":
    main()
