import m3u8
import requests
import tempfile
import functools
import re
import logging
import os
from pydub import AudioSegment
from pathlib import Path
from definitions import DATA_PATH

logger = logging.getLogger("scdownload")

client_id = "r5ELVSy3RkcjX7ilaL7n2v1Z8irA9SL8"

# url = "https://soundcloud.com/yung-bruh-3/gemstone-bullets-poppin-out-the-tech"
logger.info("Enter the Souncloud URL of the track to download: ")
url = input()

logger.info("Requesting track url: " + url)
html = requests.get(url)
track_id = re.search(r'soundcloud://sounds:(.+?)"', html.text).group(1)
logger.info("Track ID: " + track_id)

track_info_url = "https://api-v2.soundcloud.com/tracks?ids={0}&client_id={1}".format(track_id, client_id)
logger.info("Requesting track info url: " + track_info_url)
track_info_raw = requests.get(track_info_url)
track_info = track_info_raw.json()[0]

track_name = track_info["title"]
logger.info("Track name: " + track_name)

# TODO: we should change this to search specifically for the hls mp3 stream
stream_url = track_info["media"]["transcodings"][0]["url"] + "?client_id={0}".format(client_id)
logger.info("Requesting stream url: " + stream_url)
stream_info = requests.get(stream_url)

playlist_url = stream_info.json()["url"]
logger.info("Requesting playlist url: " + playlist_url)
m3u8_obj = m3u8.load(playlist_url)

logger.info("Found {0} files in playlist".format(len(m3u8_obj.files)))

files = list()
for file_url in m3u8_obj.files:
    logger.info("Requesting playlist file url: " + file_url)
    request = requests.get(file_url, stream=True)
    temp = tempfile.NamedTemporaryFile(delete=False)
    received = 0
    with temp as f:
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                received += len(chunk)
                f.write(chunk)
                f.flush()
        f.seek(0)
        files.append(AudioSegment.from_file_using_temporary_files(f, 'mp3'))

full_track = functools.reduce(lambda r,next : r+next, files)

uploader_name = track_info["user"]["username"]
logger.info("Track uploader was {0}. Press enter to continue or provide an alternative artist name: ".format(uploader_name))
custom_artist_name = input()

artist_name = uploader_name if custom_artist_name == "" else custom_artist_name
logger.info("Chosen artist name is: " + artist_name)

artist_path = os.path.join(DATA_PATH, artist_name)
Path(artist_path).mkdir(exist_ok=True)
logger.info("Artist path is: " + artist_path)

# need to remove special chars to make a valid file name
file_name = re.sub(r'(?u)[^-\w]', '', track_name.strip().replace(' ', '_')) + ".mp3"
file_path = os.path.join(artist_path, file_name)

logger.info("Exporting track to file: " + file_path)
full_track.export(file_path, format="mp3")
logger.info("Exported track \"{0}\" to file {1}".format(track_name, file_path))

metadata_file_name = "meta.txt"
metadata_file_path = os.path.join(artist_path, metadata_file_name)

logger.info("Writing metadata to file: " + metadata_file_path)
with open(metadata_file_path, "w") as metadata_file:
    # TODO: Filter the specific pieces of information we want to include
    metadata_file.write(track_info_raw.text)

artwork_url = track_info["artwork_url"]
logger.info("Requesting artwork url: " + artwork_url)
artwork_info = requests.get(artwork_url)

artwork_name, artwork_ext = os.path.splitext(artwork_url)
artwork_file_name = "artwork" + artwork_ext
artwork_file_path = os.path.join(artist_path, artwork_file_name)

logger.info("Writing artwork to file: " + artwork_file_path)
with open(artwork_file_path, "wb") as artwork_file:
    artwork_file.write(artwork_info.content)
