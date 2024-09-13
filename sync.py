import os
import shutil
import logging
import argparse
import time

def setup_logging(logfile):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(logfile),
                            logging.StreamHandler()
                        ])

def sync_folders(source, replica):
    # Creating and copying files in the source folder
    for src_dir, dirs, files in os.walk(source):
        dst_dir = src_dir.replace(source, replica, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            logging.info(f"Created directory {dst_dir}")

        for file_name in files:
            src_file = os.path.join(src_dir, file_name)
            dst_file = os.path.join(dst_dir, file_name)
            if not os.path.exists(dst_file) or os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                shutil.copy2(src_file, dst_file)
                logging.info(f"Copied file {src_file} to {dst_file}")

def main():
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('--source', required=True, help='Source folder path')
    parser.add_argument('--replica', required=True, help='Replica folder path')
    parser.add_argument('--interval', type=int, default=60, help='Synchronization interval in seconds. Default is 60 seconds')
    parser.add_argument('--logfile', default='sync.log', help='Log file path')
    
    args = parser.parse_args()
    
    setup_logging(args.logfile)
    
    while True:
        sync_folders(args.source, args.replica)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
