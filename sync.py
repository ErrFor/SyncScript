import os
import shutil
import logging
import argparse
import time
import sys
import hashlib

# Set up logging to both a file and console
def setup_logging(logfile):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(logfile),
                            logging.StreamHandler()
                        ])

# Calculate MD5 checksum for a file to check if two files are identical
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks of 512KB (524288 bytes)
            for chunk in iter(lambda: f.read(524288), b""):
                hash_md5.update(chunk)
    except Exception as e:
        # Log and exit in case of an error while calculating the hash
        logging.error(f"Error calculating MD5 for file {file_path}: {e}")
        sys.exit(1)
    return hash_md5.hexdigest()

# Synchronization of two folders
def sync_folders(source, replica):
    sync_occurred = False
    files_synced = 0  # Counter for the number of synced files
    files_removed = 0  # Counter for the number of removed files
    dirs_removed = 0  # Counter for the number of removed directories
    dirs_synced = 0  # Counter for the number of synced directories

    # Walk through the source directory to find files and directories
    for src_dir, _, files in os.walk(source):
        replica_dir = src_dir.replace(source, replica, 1)

        # Create the directory if it doesn't exist
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            logging.info(f"Copied directory {src_dir} to {replica_dir}")
            sync_occurred = True
            dirs_synced += 1

        # Copy files from the source folder to the replica
        for file_name in files:
            src_file = os.path.join(src_dir, file_name)
            replica_file = os.path.join(replica_dir, file_name)
            try:
                # Calculate the MD5 checksum of the source file
                src_md5 = calculate_md5(src_file)

                # Copy the file if it doesn't exist in the replica
                if not os.path.exists(replica_file):
                    shutil.copy2(src_file, replica_file)
                    logging.info(f"Copied file {src_file} to {replica_file}")
                    sync_occurred = True
                    files_synced += 1
                else:
                    # Compare the MD5 checksums of the source and replica files
                    replica_md5 = calculate_md5(replica_file)
                    if src_md5 != replica_md5:
                        # Modified the replica file if it is different from the source file
                        shutil.copy2(src_file, replica_file)
                        logging.info(f"Modified file {src_file} and updated {replica_file}")    
                        sync_occurred = True
                        files_synced += 1
            except PermissionError:
                logging.error(f"Permission denied: Cannot copy file {src_file} to {replica_file}. Please check your permissions.")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Error copying file {src_file} to {replica_file}: {e}")
                sys.exit(1)

    # Walk through the replica directory to find files and directories that no longer exist in the source
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
                    sync_occurred = True
                    files_removed += 1
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
                sync_occurred = True
                dirs_removed += 1
            except PermissionError:
                logging.error(f"Permission denied: Cannot remove directory {replica_dir}. Please check your permissions.")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Error removing directory {replica_dir}: {e}")
                sys.exit(1)

    return sync_occurred, files_synced, files_removed, dirs_removed, dirs_synced               

def main():
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('--source', required=True, help='Source folder path')
    parser.add_argument('--replica', required=True, help='Replica folder path')
    parser.add_argument('--interval', type=int, default=60, help='Synchronization interval in seconds. Default is 60 seconds')
    parser.add_argument('--logfile', default='sync.log', help='Log file path')
    
    args = parser.parse_args()

    setup_logging(args.logfile)
    
    try:
            # Check if source directory exists
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source folder '{args.source}' does not exist.")
            
            # Check if replica directory exists, prompt user if it does not
            if not os.path.exists(args.replica):
                create_replica = input(f"Replica folder '{args.replica}' does not exist. Do you want to create it? (y/n): ")
                if create_replica.lower() == 'y':
                    os.makedirs(args.replica)
                    logging.info(f"Created replica folder {args.replica}")
                else:
                    logging.info("Replica folder does not exist and will not be created. Exiting.")
                    sys.exit(1)

            # Main synchronization loop
            while True:
                sync_occurred, files_synced, files_removed, dirs_removed, dirs_synced = sync_folders(args.source, args.replica)
                if sync_occurred:
                    logging.info(
                        f"Synchronization completed successfully. {files_synced} files were synced, {dirs_synced} directories were synced. {files_removed} files were removed, and {dirs_removed} directories were removed."
                        )
                else:
                    logging.info("No changes detected. Synchronization not required.")

                # Sleep for the specified interval before the next sync    
                time.sleep(args.interval)
        
    except FileNotFoundError as e:
        print(e)
        logging.error(e)

if __name__ == "__main__":
    main()
