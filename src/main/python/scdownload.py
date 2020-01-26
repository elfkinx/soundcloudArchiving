import m3u8
import requests
import tempfile
import functools
import re
import logging
import os
import sys
import json
import lxml.html
from pydub import AudioSegment
from pathlib import Path
from definitions import DATA_PATH


def get_html(url, stream=False):
    response = requests.get(url, stream=stream)
    if response.status_code != 200:
        logger.error("Received error reponse {0} when requesting URL {1}".format(response.status_code, url))
        sys.exit(1)
    return response

def get_playlist_name(page_html):
    xml = lxml.html.fromstring(page_html)
    names = xml.xpath("//meta[@property='twitter:title']")
    playlist_name = names[0].attrib["content"]
    return playlist_name

def get_playlist_info(playlist_id, client_id):
    logger.info("Playlist ID: "+ playlist_id)
    playlist_info_url = "https://api.soundcloud.com/playlists/{0}/tracks?client_id={1}".format(playlist_id, client_id)
    logger.info("Requesting playlist info url: " + playlist_info_url)
    playlist_info_response = get_html(playlist_info_url)
    playlist_info_json = playlist_info_response.json()
    logger.info("Found {0} tracks in playlist".format(len(playlist_info_json)))
    return playlist_info_json

def get_track_info(track_id, client_id):
    logger.info("Track ID: " + track_id)
    track_info_url = "https://api-v2.soundcloud.com/tracks?ids={0}&client_id={1}".format(track_id, client_id)
    logger.info("Requesting track info url: " + track_info_url)
    track_info_json = get_html(track_info_url).json()
    assert len(track_info_json) == 1, "More than one track infos received for url"
    return track_info_json[0]

def get_stream_info(track_info, client_id):
    transcodings = track_info["media"]["transcodings"]
    matches = list(filter(lambda x: x["format"] == {"protocol": "hls", "mime_type": "audio/mpeg"}, transcodings))
    assert len(matches) == 1, "Did not find transcoding with required format "+ transcodings
    stream_url = matches[0]["url"] + "?client_id={0}".format(client_id)
    logger.info("Requesting stream url: " + stream_url)
    stream_info = get_html(stream_url)
    return stream_info

def get_track(track_info, client_id):
    playlist_url = get_stream_info(track_info, client_id).json()["url"]
    logger.info("Requesting playlist url: " + playlist_url)

    m3u8_obj = m3u8.load(playlist_url)
    logger.info("Found {0} files in playlist".format(len(m3u8_obj.files)))

    files = list()
    for file_url in m3u8_obj.files:
        logger.info("Requesting playlist file url: " + file_url)
        request = get_html(file_url, stream=True)
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

    full_track = functools.reduce(lambda r, next: r + next, files)
    return full_track

def get_artist_name(uploader_name, custom_artist_fn):
    custom_artist_name = custom_artist_fn()
    artist_name = uploader_name if custom_artist_name == "" else custom_artist_name
    return artist_name

def get_track_path(artist_name, album_name, track_name):
    artist_path = os.path.join(DATA_PATH, artist_name)
    Path(artist_path).mkdir(exist_ok=True)
    album_path = os.path.join(artist_path, album_name)
    Path(album_path).mkdir(exist_ok=True)
    # need to remove special chars to make a valid file name
    track_name_clean = re.sub(r'(?u)[^-\w]', '', track_name.strip().replace(' ', '_'))
    track_path = os.path.join(album_path, track_name_clean)
    Path(track_path).mkdir(exist_ok=True)
    return track_path


def export_track(full_track, track_path, file_name):
    file_path = os.path.join(track_path, file_name)
    logger.info("Exporting track to file: " + file_path)
    full_track.export(file_path, format="mp3")
    logger.info("Exported track to file {0}".format(file_path))


def export_metadata(track_info, track_path, file_name):
    file_path = os.path.join(track_path, file_name)
    logger.info("Writing metadata to file: " + file_path)
    with open(file_path, "w") as metadata_file:
        # TODO: Filter the specific pieces of information we want to include
        metadata_file.write(json.dumps(track_info))

def process_custom_metadata(metadata, client_id, track_id, track_info, track_path, file_name):
    results = {}
    for key in metadata:
        if key == "playlists":
            results[key] = get_playlists_metadata(client_id)
        elif key == "albums":
            results[key] = get_albums_metadata(client_id)
        elif key == "background":
            export_background_image(track_id, track_path)


def export_background_image(track_id, track_path, filename="background.jpg"):
    # TODO: Verify the image url by searching for it in the html content
    background_image_url = "https://va.sndcdn.com/bg/soundcloud:tracks:{0}/soundcloud-tracks-{0}.jpg".format(track_id)
    logging.info("Requesting background image from url: "+ background_image_url)
    background_image_info = get_html(background_image_url)
    export_image(background_image_info.content, track_path, filename)
    logging.info("Written background image")

def get_playlists_metadata(client_id):
    # TODO: Limit should be configurable? First 1000 should be enough
    playlists_url = "https://api-v2.soundcloud.com/tracks/646284687/playlists_without_albums?representation=mini&" \
                    "client_id={0}&limit=1000".format(client_id)
    logging.info("Requesting playlists metadata from url: "+ playlists_url)
    playlists_info = get_html(playlists_url)
    playlist_names = list(map(lambda x: x["title"], playlists_info.json()["collection"]))
    logging.info("Got playlist names: "+ str(playlist_names))
    return playlist_names


def get_albums_metadata(client_id):
    # TODO: Limit should be configurable? First 1000 should be enough
    albums_url = "https://api-v2.soundcloud.com/tracks/646284687/albums?representation=mini&" \
                    "client_id={0}&limit=1000".format(client_id)
    logging.info("Requesting albums metadata from url: "+ albums_url)
    albums_info = get_html(albums_url)
    album_names = list(map(lambda x: x["title"], albums_info.json()["collection"]))
    logging.info("Got album names: "+ str(album_names))
    return album_names


def export_image(artwork, track_path, file_name):
    image_file_path = os.path.join(track_path, file_name)
    logger.info("Writing image to file: " + image_file_path)
    with open(image_file_path, "wb") as image_file:
        image_file.write(artwork)


def archive_track(track_id, client_id, custom_artist_fn, metadata, album_name="Singles"):
    track_info = get_track_info(track_id, client_id)

    track_name = track_info["title"]
    logger.info("Track name: " + track_name)

    full_track = get_track(track_info, client_id)

    uploader_name = track_info["user"]["username"]
    logger.info(
        "Track uploader was {0}. Press enter to continue or provide an alternative artist name: ".format(uploader_name))

    artist_name = get_artist_name(uploader_name, custom_artist_fn)
    logger.info("Chosen artist name is: " + artist_name)

    track_path = get_track_path(artist_name, album_name, track_name)
    logger.info("Track path is: " + track_path)

    export_track(full_track, track_path, "track.mp3")

    if metadata == []:
        export_metadata(track_info, track_path, "meta.txt")
    else:
        process_custom_metadata(metadata, client_id, track_id, track_info, track_path, "meta.txt")

    artwork_url = track_info["artwork_url"]
    logger.info("Requesting artwork url: " + artwork_url)
    artwork_info = get_html(artwork_url)

    artwork_name, artwork_ext = os.path.splitext(artwork_url)
    artwork_file_name = "artwork" + artwork_ext

    export_image(artwork_info.content, track_path, artwork_file_name)


logger = logging.getLogger("scdownload")

client_id = "r5ELVSy3RkcjX7ilaL7n2v1Z8irA9SL8"


def download(url, custom_artist_fn, metadata=[]):
    logger.info("Requesting SoundCloud url: " + url)
    response = get_html(url)

    track_search = re.search(r'soundcloud://sounds:(.+?)"', response.text)
    playlist_search = re.search(r'soundcloud://playlists:(.+?)"', response.text)

    if track_search != None:
        track_id = track_search.group(1)
        logger.info("Found track ID {0} on page. Dowloading track...".format(track_id))
        archive_track(track_id, client_id, custom_artist_fn, metadata)
        return 0
    elif playlist_search != None:
        playlist_id = playlist_search.group(1)
        logger.info("Found playlist ID {0} on page. Downloading playlist...".format(playlist_id))
        playlist_name = get_playlist_name(response.content)
        logger.info("Playlist name: " + playlist_name)
        playlist_info = get_playlist_info(playlist_id, client_id)
        for track_info in playlist_info:
            archive_track(str(track_info["id"]), client_id, custom_artist_fn, metadata, album_name=playlist_name)
        return 0
    else:
        logger.error("No valid track or playlist ID found on page. Is this a valid SoundCloud link?")
        return -1

def run_cmdline():
    # url = "https://soundcloud.com/yung-bruh-3/gemstone-bullets-poppin-out-the-tech"
    logger.info("Enter the SoundCloud URL of the track/playlist to download: ")
    soundcloud_url = input()
    result = download(soundcloud_url, input)
    if (result < 0):
        sys.exit(result)