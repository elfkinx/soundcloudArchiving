"""
scdownload (SoundCloud Downloader)

This file contains prototype code / examples of how additional functionality can be implemented

The use of the soundcloud API is very restricted. In order to use certain custom functionality you must be registered
 as a soundcloud developer and/or authenticate using their OAuth API. This set-up would be prohibitive for most users
 and much of the data can be gotten from the raw HTTP requests that the HTML pages send.

Below includes some of the functionality that could be additionally supported if developer registration and
authentication was completed

#######################################################################################################################

Uploading (adapted from https://developers.soundcloud.com/docs#uploading example)

def all_files_in(self, path, files=[]):
    for next in os.listdir(path):
        files.append(next)
        next_path = os.path.join(path, next)
        if os.path.isdir(next_path):
            self.all_files_iter(next_path, files)

# create a client object with access token
client = soundcloud.Client(access_token='YOUR_ACCESS_TOKEN')

all_tracks = all_files_in(DATA_ROOT)

for track in all_tracks:
    # upload audio file
    uploaded_track = client.post('/tracks', track={
        'title': track,
        'asset_data': open(track, 'rb')
    })

#######################################################################################################################

"""