import os
import shutil
import logging
import argparse
import time
import sys
import hashlib

def setup_logging(logfile):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(logfile),
                            logging.StreamHandler()
                        ])

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        logging.error(f"Error calculating MD5 for file {file_path}: {e}")
        sys.exit(1)
    return hash_md5.hexdigest()

def sync_folders(source, replica):
    # Synchronization: create and copy files
    for src_dir, _, files in os.walk(source):
        # Getting the appropriate directory in the replica
        replica_dir = src_dir.replace(source, replica, 1)
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            logging.info(f"Created directory {replica_dir}")

        # Copy files from the source folder to the replica
        for file_name in files:
            src_file = os.path.join(src_dir, file_name)
            replica_file = os.path.join(replica_dir, file_name)
            try:
                src_md5 = calculate_md5(src_file)
                if not os.path.exists(replica_file):
                    shutil.copy2(src_file, replica_file)
                    logging.info(f"Copied file {src_file} to {replica_file}")
                else:
                    replica_md5 = calculate_md5(replica_file)
                    if src_md5 != replica_md5:
                        shutil.copy2(src_file, replica_file)
                        logging.info(f"Modified file {src_file} and updated {replica_file}")    
            except PermissionError:
                logging.error(f"Permission denied: Cannot copy file {src_file} to {replica_file}. Please check your permissions.")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Error copying file {src_file} to {replica_file}: {e}")
                sys.exit(1)

    # Deleting files and folders that are not in the source folder
    for replica_dir, _, files in os.walk(replica, topdown=False):
        src_dir = replica_dir.replace(replica, source, 1)

        # Deleting files
        for file_name in files:
            replica_file = os.path.join(replica_dir, file_name)
            src_file = os.path.join(src_dir, file_name)
            if not os.path.exists(src_file):
                try:
                    os.remove(replica_file)
                    logging.info(f"Removed file {replica_file}")
                except PermissionError:
                    logging.error(f"Permission denied: Cannot remove file {replica_file}. Please check your permissions.")
                    sys.exit(1)
                except Exception as e:
                    logging.error(f"Error removing file {replica_file}: {e}")
                    sys.exit(1)

        # Deleting directories
        if not os.path.exists(src_dir):
            try:
                shutil.rmtree(replica_dir)
                logging.info(f"Removed directory {replica_dir}")
            except PermissionError:
                logging.error(f"Permission denied: Cannot remove directory {replica_dir}. Please check your permissions.")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Error removing directory {replica_dir}: {e}")
                sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('--source', required=True, help='Source folder path')
    parser.add_argument('--replica', required=True, help='Replica folder path')
    parser.add_argument('--interval', type=int, default=60, help='Synchronization interval in seconds. Default is 60 seconds')
    parser.add_argument('--logfile', default='sync.log', help='Log file path')
    
    args = parser.parse_args()
    
    try:
            # Check if source directory exists
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source folder '{args.source}' does not exist.")
            
            # Check if replica directory exists
            if not os.path.exists(args.replica):
                raise FileNotFoundError(f"Replica folder '{args.replica}' does not exist.")

            setup_logging(args.logfile)
            
            while True:
                sync_folders(args.source, args.replica)
                time.sleep(args.interval)
        
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
