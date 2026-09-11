import zipfile
import os

zip_path = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2010.zip"
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print("Files in zip:")
        for name in zip_ref.namelist():
            print("  ", name)
else:
    print("Zip file does not exist!")
