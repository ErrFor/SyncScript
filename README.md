# SyncScript

This Python script synchronizes two folders: `source` and `replica`. The goal of the script is to ensure that the `replica` folder is always an exact copy of the `source` folder. The synchronization is one-way, meaning that any changes in the `source` folder are reflected in the `replica`, but not the other way around. The script supports periodic synchronization and logs all file operations (creation, copying, deletion) to both the console and a log file.

## Features

- **One-way synchronization:** The `replica` folder is updated to match the content of the `source` folder.
- **Periodic synchronization:** You can specify an interval for how often synchronization should occur.
- **File logging:** All file operations (creation, copying, and removal) are logged to a file and printed in the console.
- **Customizable parameters:** Folder paths, synchronization interval, and log file path can be provided as command line arguments.
- **No third-party synchronization libraries:** The script uses only built-in Python libraries for file and folder operations.

## Requirements

- Python 3.x

## Usage

Run the script from the command line by providing the required arguments: `--source`, `--replica`, `--interval`, and optionally `--logfile`.

### Example command:

```bash
python sync_folders.py --source <source_folder_path> --replica <replica_folder_path> --interval <interval_in_seconds> --logfile <logfile_path>
```

### Arguments

- `--source` (required): The path to the source folder you want to synchronize.
- `--replica` (required): The path to the replica folder that will be synchronized with the source.
- `--interval` (optional): The time interval (in seconds) between synchronizations. The default is 60 seconds.
- `--logfile` (optional): The path to the log file where operations will be recorded. The default is `sync.log` in the current directory.

### Example

```bash
python sync_folders.py --source /path/to/source --replica /path/to/replica --interval 120 --logfile /path/to/logfile.log
```

This command will:

- Synchronize the contents of `/path/to/replica` with `/path/to/source`.
- Synchronize every 120 seconds.
- Log all operations to `/path/to/logfile.log`.
