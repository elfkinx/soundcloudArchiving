import m3u8
import requests
import tempfile
import functools
from pydub import AudioSegment
import re

client_id = "r5ELVSy3RkcjX7ilaL7n2v1Z8irA9SL8"
url = "https://soundcloud.com/yung-bruh-3/gemstone-bullets-poppin-out-the-tech"

html = requests.get(url)
track_id = re.search(r'soundcloud://sounds:(.+?)"', html.text).group(1)

track_info_url = "https://api-v2.soundcloud.com/tracks?ids={0}&client_id={1}".format(track_id, client_id)
track_info = requests.get(track_info_url)
track_name = track_info.json()[0]["title"]
stream_url = track_info.json()[0]["media"]["transcodings"][0]["url"] # We should change this to search for the hls mp3 stream
stream_info = requests.get(stream_url + "?client_id={0}".format(client_id))
playlist_url = stream_info.json()["url"]

m3u8_obj = m3u8.load(playlist_url)
files = list()
for file_name in m3u8_obj.files:
    request = requests.get(file_name, stream=True)
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

file_name = re.sub(r'(?u)[^-\w]', '', track_name.strip().replace(' ', '_')) + ".mp3" # need to remove special chars to make a valid file name

full_track = functools.reduce(lambda r,next : r+next, files)
full_track.export(file_name, format="mp3")
print("Written track \"{0}\" to file {1}".format(track_name, file_name))