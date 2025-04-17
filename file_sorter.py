#!/usr/bin/env python3
"""
Project Title: FileSorter

Organizes files in a source directory into categorized subfolders by MIME type or extension.

Supports cross-platform sorting with CLI options for mode, renaming, and logging.

Author: Kris Armstrong
"""
import argparse
import logging
import mimetypes
import os
import shutil
from datetime import datetime
from filecmp import cmp
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from PIL import Image
import magic

__version__ = "1.0.2"

class Config:
    """Global constants for FileSorter."""
    LOG_FILE: str = "file_sorter.log"
    ENCODING: str = "utf-8"
    IMAGE_MIN_WIDTH: int = 100
    IMAGE_MIN_HEIGHT: int = 100

def setup_logging(verbose: bool, logfile: str = Config.LOG_FILE) -> None:
    """Configure logging with rotating file handler.

    Args:
        verbose: Enable DEBUG level logging if True.
        logfile: Path to log file.

    Raises:
        PermissionError: If log file cannot be written.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(logfile, maxBytes=1048576, backupCount=3),
            logging.StreamHandler(),
        ],
    )

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Organize files by MIME type or extension.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source",
        default=str(Path.home() / "Downloads"),
        help="Source directory to organize",
    )
    parser.add_argument(
        "--target",
        default=str(Path.home() / "Documents"),
        help="Target directory for categorized subfolders",
    )
    parser.add_argument(
        "--mode",
        choices=["mime", "extension"],
        default="mime",
        help="Sorting mode: MIME type or extension",
    )
    parser.add_argument(
        "--rename",
        action="store_true",
        help="Rename files with YYYY-MM- prefix (default for extension mode)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--logfile",
        default=Config.LOG_FILE,
        help="Log file path",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()

def create_directories(target: str) -> None:
    """Create subfolders for file types if they don't exist.

    Args:
        target: Base directory for subfolders.

    Raises:
        OSError: If directories cannot be created.
    """
    directories = [
        "Images", "Videos", "Music", "Compressed", "PDF", "Word", "Excel",
        "Presentations", "Disk_Images", "PCAP", "Others", "Code", "Text",
        "Ebooks", "Executables", "Calendar", "Conf", "No_Extension"
    ]
    logging.info("Creating subdirectories in %s", target)
    for directory in directories:
        try:
            os.makedirs(os.path.join(target, directory), exist_ok=True)
            logging.debug("Created or verified directory: %s", directory)
        except OSError as e:
            logging.error("Failed to create directory %s: %s", directory, e)
            raise

def is_useful_image(file_path: str) -> bool:
    """Check if an image meets minimum size requirements.

    Args:
        file_path: Path to image file.

    Returns:
        True if image is useful, False otherwise.
    """
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            return width >= Config.IMAGE_MIN_WIDTH and height >= Config.IMAGE_MIN_HEIGHT
    except Exception as e:
        logging.error("Error processing image %s: %s", file_path, e)
        return False

def get_year_month_prefix(file_path: str) -> str:
    """Return a 'YYYY-MM' prefix based on file's last modification time.

    Args:
        file_path: Path to file.

    Returns:
        Formatted 'YYYY-MM' string.
    """
    try:
        timestamp = os.path.getmtime(file_path)
    except OSError as e:
        logging.warning("Could not get mtime for %s: %s", file_path, e)
        timestamp = datetime.now().timestamp()
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m")

def get_destination_folder(file_path: str, mode: str, target: str) -> tuple[str, Optional[str]]:
    """Determine destination folder and optional new filename based on mode.

    Args:
        file_path: Source file path.
        mode: Sorting mode ('mime' or 'extension').
        target: Base directory for subfolders.

    Returns:
        Tuple of destination folder path and optional new filename (with prefix or None).
    """
    file_name = os.path.basename(file_path)
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()

    if mode == "extension":
        folder = file_extension.lstrip(".") or "No_Extension"
        new_name = f"{get_year_month_prefix(file_path)}-{file_name}" if file_extension else file_name
        return os.path.join(target, folder), new_name

    # MIME mode
    try:
        file_type = magic.from_file(file_path, mime=True)
    except Exception as e:
        logging.error("Failed to detect MIME type for %s: %s", file_path, e)
        file_type = None

    mime_mapping = {
        "image/": "Images",
        "video/": "Videos",
        "audio/": "Music",
        "application/zip": "Compressed",
        "application/x-tar": "Compressed",
        "application/x-gzip": "Compressed",
        "application/x-bzip2": "Compressed",
        "application/x-7z-compressed": "Compressed",
        "application/x-rar-compressed": "Compressed",
        "application/pdf": "PDF",
        "application/msword": "Word",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
        "application/vnd.ms-excel": "Excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
        "application/vnd.ms-powerpoint": "Presentations",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "Presentations",
        "application/x-iso9660-image": "Disk_Images",
        "application/x-apple-diskimage": "Disk_Images",
        "application/vnd.tcpdump.pcap": "PCAP",
        "application/x-pcapng": "PCAP",
        "text/x-python": "Code",
        "application/javascript": "Code",
        "text/html": "Code",
        "text/css": "Code",
        "text/x-shellscript": "Code",
        "application/x-sh": "Code",
        "text/plain": "Text",
        "text/markdown": "Text",
        "application/epub+zip": "Ebooks",
        "application/x-msdownload": "Executables",
        "text/calendar": "Calendar",
    }
    extension_mapping = {
        ".pcap": "PCAP",
        ".pcapng": "PCAP",
        ".txt": "Text",
        ".conf": "Conf",
    }

    if file_type:
        for mime, folder in mime_mapping.items():
            if file_type.startswith(mime) or file_type == mime:
                if file_type.startswith("image/") and not is_useful_image(file_path):
                    logging.info("Deleting useless image: %s", file_path)
                    os.remove(file_path)
                    return "", None
                return os.path.join(target, folder), None
    return os.path.join(target, extension_mapping.get(file_extension, "Others")), None

def move_file(file_path: str, destination_folder: str, new_name: Optional[str] = None) -> bool:
    """Move a file to the destination folder, handling duplicates.

    Args:
        file_path: Source file path.
        destination_folder: Destination folder path.
        new_name: Optional new filename (e.g., with date prefix).

    Returns:
        True if file was moved or deleted, False on error.
    """
    if not destination_folder:  # Image deleted
        return True
    file_name = new_name or os.path.basename(file_path)
    destination_path = os.path.join(destination_folder, file_name)
    logging.debug("Attempting to move %s to %s", file_path, destination_path)

    if os.path.exists(destination_path):
        try:
            if cmp(file_path, destination_path, shallow=False):
                logging.info("Deleting duplicate file: %s", file_path)
                os.remove(file_path)
                return True
            source_mtime = os.path.getmtime(file_path)
            destination_mtime = os.path.getmtime(destination_path)
            if source_mtime > destination_mtime:
                logging.info("Replacing older file: %s with newer: %s", destination_path, file_path)
                os.remove(destination_path)
            else:
                logging.info("Deleting older file: %s", file_path)
                os.remove(file_path)
                return True
        except Exception as e:
            logging.error("Error comparing or deleting %s: %s", file_path, e)
            return False

    try:
        shutil.move(file_path, destination_path)
        logging.info("Moved %s to %s", file_path, destination_path)
        return True
    except Exception as e:
        logging.error("Error moving %s to %s: %s", file_path, destination_path, e)
        return False

def organize_files(source: str, target: str, mode: str, rename: bool) -> None:
    """Organize files in the source directory.

    Args:
        source: Source directory path.
        target: Target directory for subfolders.
        mode: Sorting mode ('mime' or 'extension').
        rename: Add YYYY-MM- prefix (forced True for extension mode).

    Raises:
        FileNotFoundError: If source directory doesn’t exist.
        OSError: If file operations fail.
    """
    if not os.path.isdir(source):
        raise FileNotFoundError(f"Source directory not found: {source}")

    create_directories(target)
    rename = rename or mode == "extension"

    for filename in os.listdir(source):
        file_path = os.path.join(source, filename)
        if not os.path.isfile(file_path):
            continue
        try:
            destination_folder, new_name = get_destination_folder(file_path, mode, target)
            if rename and new_name is None:
                new_name = f"{get_year_month_prefix(file_path)}-{filename}"
            move_file(file_path, destination_folder, new_name)
        except Exception as e:
            logging.error("Error processing %s: %s", file_path, e)

def main() -> int:
    """Main entry point for FileSorter.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_args()
    setup_logging(args.verbose, args.logfile)
    try:
        organize_files(args.source, args.target, args.mode, args.rename)
        return 0
    except KeyboardInterrupt:
        logging.info("Cancelled by user")
        return 0
    except Exception as e:
        logging.error("Error: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())