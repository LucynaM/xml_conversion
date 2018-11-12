import zipfile
from django.conf import settings

def handle_zip_file(file):
    with zipfile.ZipFile(file.path, allowZip64=True) as zip_file:
        names = zip_file.namelist()
        for name in names:
            if name.endswith(('.xml', '.XML', )):
                file_name = name
        unzipped_file = zip_file.extract(file_name, settings.MEDIA_ROOT)
    zip_file.close()
    return unzipped_file