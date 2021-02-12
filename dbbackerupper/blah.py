from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os

# Below code does the authentication
# part of the code
gauth = GoogleAuth()

# Creates local webserver and auto
# handles authentication.
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# replace the value of this variable
# with the absolute path of the directory
path = r"/home/ubuntu/foo"

# iterating thought all the files/folder
# of the desired directory
for x in os.listdir(path):
    file = drive.CreateFile({'title': x})
    file.SetContentFile(os.path.join(path, x))
    file.Upload()

    # Due to a known bug in pydrive if we
    # don't empty the variable used to
    # upload the files to Google Drive the
    # file stays open in memory and causes a
    # memory leak, therefore preventing its
    # deletion
    file = None
