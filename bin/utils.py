import zipfile
import os

def zip_files(zip_file_name, saved_dir, files_to_zip):
    with zipfile.ZipFile(os.path.join(saved_dir,zip_file_name), 'w') as zipMe:        
        for file in files_to_zip:
            zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)
def unzip_file(tmp_dir_to_unzip, zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zipFile:
        zipFile.extractall(tmp_dir_to_unzip)
