import os
import csv
import subprocess
import shutil
import logging
from datetime import datetime
# Setup logging
logging.basicConfig(filename='compress_long_paths.log', level=logging.INFO)

def log_directory_files(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            logging.info('File: %s, Size: %s bytes, Modified: %s', file_path, file_size, modified_time)

def find_long_paths(root_folder, adjusted_limit):
    long_paths = []
    for root, _, files in os.walk(root_folder):
        for file in files:
            full_path = os.path.join(root, file)
            if len(full_path) > adjusted_limit:
                long_paths.append(full_path)
    return long_paths

def unique_parent_dirs(paths):
    return set(os.path.dirname(path) for path in paths)

def write_to_csv(dirs_list, csv_file):
    sorted_dirs = sorted(dirs_list, reverse=True)  # Sort in descending order
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Unique Parent Directories"])
        for dir_path in sorted_dirs:
            writer.writerow([dir_path])

def main():
    csv_file = 'parent_dirs_to_compress.csv'
    long_paths = find_long_paths('Z:\\', 210)  # Update these parameters
    unique_dirs = unique_parent_dirs(long_paths)
    write_to_csv(unique_dirs, csv_file)
    logging.info('Written unique directories to %s', csv_file)

    for dir_path in unique_dirs:
        if os.path.exists(dir_path):
            log_directory_files(dir_path)  # Log the file details
            logging.info('User input for %s: %s', dir_path, user_input)
            zip_path = f"{dir_path}.zip"
            completed_process = subprocess.run([r"C:\Program Files\7-Zip\7z.exe", "a", "-tzip", zip_path, f"{dir_path}\\*"], capture_output=True, text=True, check=True)
            logging.info('7-Zip output for %s: %s', dir_path, completed_process.stdout)
            if "WARNINGS" in completed_process.stdout or "WARNINGS" in completed_process.stderr:
                print("7-Zip threw warnings. Aborting.")
                logging.warning('7-Zip threw warnings for %s. Aborting.', dir_path)
                return

            if os.path.getsize(zip_path) < 4096:
                print("Compression to ZIP had an error. Check if the original folder is still intact. Aborting.")
                logging.warning('Compression to ZIP had an error for %s. Aborting.', dir_path)
                return

            shutil.rmtree(dir_path)
            print(f"Successfully compressed and deleted {dir_path}.")
            logging.info('Successfully compressed and deleted %s.', dir_path)
        else:
            print(f"The directory {dir_path} does not exist. Skipping.")
            logging.warning('The directory %s does not exist. Skipping.', dir_path)

if __name__ == '__main__':
    main()
