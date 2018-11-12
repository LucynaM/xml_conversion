import zipfile
import os

def handle_zip_file(file):
    with zipfile.ZipFile(file.path, allowZip64=True) as zip_file:
        names = zip_file.namelist()
        for name in names:
            if name.endswith(('.xml', '.XML', )):
                file_name = name
                print(file_name)
        unzipped_file = zip_file.extract(file_name, file.path.url[1:7])
    zip_file.close()
    return unzipped_file