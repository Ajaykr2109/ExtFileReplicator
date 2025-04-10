import os
import shutil
import hashlib


class FileOperations:
    @staticmethod
    def safe_copy(src, dest):
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
        try:
            if os.path.getsize(file1) != os.path.getsize(file2):
                return False

            return FileOperations.file_hash(file1) == FileOperations.file_hash(file2)
        except:
            return False

    @staticmethod
    def file_hash(filepath):
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None

    @staticmethod
    def ensure_directory_exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
