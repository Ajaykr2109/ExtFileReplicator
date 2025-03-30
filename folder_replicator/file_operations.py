import os
import shutil
import hashlib


class FileOperations:
    @staticmethod
    def safe_copy(src, dest):
        """Copy file with error handling"""
        try:
            shutil.copy2(src, dest)
            return True
        except PermissionError:
            print(f"Permission denied on: {src}")
        except Exception as e:
            print(f"Error copying {src}: {e}")
        return False

    @staticmethod
    def files_identical(file1, file2):
        """Check if two files are identical using size and hash"""
        try:
            # First check file sizes
            if os.path.getsize(file1) != os.path.getsize(file2):
                return False

            # Then compare hashes if sizes match
            return FileOperations.file_hash(file1) == FileOperations.file_hash(file2)
        except:
            return False

    @staticmethod
    def file_hash(filepath):
        """Calculate file hash for change detection"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(65536)  # Read in 64k chunks
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None

    @staticmethod
    def ensure_directory_exists(path):
        """Create directory if it doesn't exist"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
