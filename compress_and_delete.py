import os
import shutil
import logging
from zipfile import ZipFile
from pathlib import Path

logging.basicConfig(filename='compress_and_delete.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def scan_compress_delete(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if len(dir_path) > 180:
                zip_path = dir_path + ".zip"
                parent_dir = os.path.dirname(zip_path)
                Path(parent_dir).mkdir(parents=True, exist_ok=True)
                
                with ZipFile(zip_path, 'w') as zipf:
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), dir_path))
                            logging.info(f"Compressed {os.path.join(root, file)} to {zip_path}")

                try:
                    shutil.rmtree(dir_path)
                    logging.info(f"Deleted {dir_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {dir_path}: {e}")

base_dir = input("Please provide the base directory path: ")
scan_compress_delete(base_dir)
