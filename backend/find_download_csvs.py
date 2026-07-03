import os
import glob

downloads_path = r"C:\Users\dhanr\Downloads"

def find_csvs():
    if not os.path.exists(downloads_path):
        print(f"Downloads path not found at {downloads_path}")
        return
        
    print(f"Searching for CSV files in {downloads_path}...")
    csv_files = glob.glob(os.path.join(downloads_path, "*.csv"))
    if not csv_files:
        print("No CSV files found in Downloads.")
        return
        
    for f in csv_files:
        size = os.path.getsize(f)
        modified_time = os.path.getmtime(f)
        from datetime import datetime
        mod_date = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f" - {os.path.basename(f)} (Size: {size} bytes, Modified: {mod_date})")

if __name__ == "__main__":
    find_csvs()
