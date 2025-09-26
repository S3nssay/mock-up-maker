import os
import shutil
from pathlib import Path
from typing import List, Optional
import hashlib
from datetime import datetime


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove/replace invalid characters
    invalid_chars = '<>:"|?*\\/\n\r\t'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Replace multiple underscores with single
    while "__" in filename:
        filename = filename.replace("__", "_")

    # Limit length
    filename = filename[:max_length]

    # Remove trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure filename is not empty
    return filename or "unnamed"


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if necessary"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """Get unique filename by adding counter if file exists"""
    directory = ensure_directory(directory)
    base_path = directory / f"{base_name}.{extension}"

    if not base_path.exists():
        return base_path

    counter = 1
    while True:
        unique_path = directory / f"{base_name}_{counter:03d}.{extension}"
        if not unique_path.exists():
            return unique_path
        counter += 1


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calculate hash of file contents"""
    hash_func = getattr(hashlib, algorithm)()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    return file_path.stat().st_size / (1024 * 1024)


def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
    """Create backup of file with timestamp"""
    if not file_path.exists():
        return None

    if backup_dir is None:
        backup_dir = file_path.parent / "backups"

    backup_dir = ensure_directory(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    return backup_path


def cleanup_temp_files(temp_dir: Path, max_age_hours: int = 24) -> int:
    """Clean up temporary files older than max_age_hours"""
    if not temp_dir.exists():
        return 0

    current_time = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0

    for file_path in temp_dir.rglob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except OSError:
                    pass

    return cleaned_count


def get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes"""
    total_size = 0

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size


def find_duplicate_files(directory: Path) -> List[List[Path]]:
    """Find duplicate files in directory based on content hash"""
    hash_to_files = {}

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            file_hash = calculate_file_hash(file_path)
            if file_hash not in hash_to_files:
                hash_to_files[file_hash] = []
            hash_to_files[file_hash].append(file_path)

    # Return groups of duplicates
    duplicates = [files for files in hash_to_files.values() if len(files) > 1]
    return duplicates


def safe_copy_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """Safely copy file with error handling"""
    try:
        if dst.exists() and not overwrite:
            # Create unique filename
            dst = get_unique_filename(dst.parent, dst.stem, dst.suffix.lstrip('.'))

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(src, dst)
        return True

    except Exception as e:
        print(f"Error copying {src} to {dst}: {e}")
        return False


def get_available_space(path: Path) -> int:
    """Get available disk space in bytes"""
    try:
        stat = shutil.disk_usage(path)
        return stat.free
    except Exception:
        return 0


def validate_path_length(path: Path, max_length: int = 260) -> bool:
    """Validate if path length is within OS limits"""
    return len(str(path)) <= max_length


class DirectoryManager:
    """Context manager for temporary directory operations"""

    def __init__(self, base_dir: Path, cleanup_on_exit: bool = True):
        self.base_dir = ensure_directory(base_dir)
        self.cleanup_on_exit = cleanup_on_exit
        self.created_dirs = set()
        self.created_files = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_on_exit:
            self.cleanup()

    def create_subdir(self, name: str) -> Path:
        """Create subdirectory and track it"""
        subdir = ensure_directory(self.base_dir / sanitize_filename(name))
        self.created_dirs.add(subdir)
        return subdir

    def create_file(self, name: str, content: bytes) -> Path:
        """Create file and track it"""
        file_path = self.base_dir / sanitize_filename(name)

        with open(file_path, 'wb') as f:
            f.write(content)

        self.created_files.add(file_path)
        return file_path

    def cleanup(self):
        """Clean up created files and directories"""
        # Remove files
        for file_path in self.created_files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass

        # Remove directories (in reverse order)
        for dir_path in sorted(self.created_dirs, key=lambda p: len(str(p)), reverse=True):
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except Exception:
                pass