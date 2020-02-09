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

# Limit for e.g. num comments, albums, playlists, etc. to request
request_limit = 100


def get_html(url, stream=False, fail_on_error=True):
    response = requests.get(url, stream=stream)
    if response.status_code != 200:
        logger.error("Received error reponse {0} when requesting URL {1}".format(response.status_code, url))
        if fail_on_error:
            sys.exit(1)
    return response


def get_playlist_name(page_html):
    xml = lxml.html.fromstring(page_html)
    names = xml.xpath("//meta[@property='twitter:title']")
    playlist_name = names[0].attrib["content"]
    return playlist_name


def get_playlist_info(playlist_id, client_id):
    playlist_info_url = "https://api.soundcloud.com/playlists/{0}?client_id={1}".format(playlist_id, client_id)
    logging.info("Requesting playlist info from URL: "+ playlist_info_url)
    playlist_info = get_html(playlist_info_url)
    playlist_data = playlist_info.json()
    logging.info("Got playlist info: "+ str(playlist_data))
    return playlist_data

# def get_playlist_tracks_info(playlist_id, client_id):
#     logger.info("Playlist ID: "+ playlist_id)
#     playlist_info_url = "https://api.soundcloud.com/playlists/{0}/tracks?client_id={1}".format(playlist_id, client_id)
#     logger.info("Requesting playlist info url: " + playlist_info_url)
#     playlist_info_response = get_html(playlist_info_url)
#     playlist_info_json = playlist_info_response.json()
#     logger.info("Found {0} tracks in playlist".format(len(playlist_info_json)))
#     return playlist_info_json


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


def get_path(base_path, dir):
    dir_name_clean = dir.replace('.', '')
    dir_path = os.path.join(base_path, dir_name_clean)
    Path(dir_path).mkdir(exist_ok=True)
    return dir_path


def get_track_path(artist_path, album_name, track_name):
    album_path = os.path.join(artist_path, album_name)
    Path(album_path).mkdir(exist_ok=True)
    # remove special chars to make a valid file name
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
        metadata_file.write(json.dumps(track_info))
    logging.info("Written metadata to file: "+ file_path)


def get_playlist_metadata(metadata, client_id, playlist_info, playlist_path):
    results = {}
    additional_info = get_additional_playlist_info(playlist_info, client_id)
    for key in metadata:
        if key == "artist":
            results[key] = playlist_info['user']['permalink']
        elif key == "cover_art":
            if playlist_info['artwork_url']:
                export_artwork(playlist_info['artwork_url'], playlist_path)
        elif key == "date":
            results[key] = playlist_info['created_at']
        elif key == "description":
            results[key] = playlist_info['description']
        elif key == "length":
            results[key] = playlist_info['duration']
        elif key == "likes":
            results[key] = additional_info['likes_count']
        elif key == "reposts":
            results[key] = additional_info['reposts_count']
        elif key == "tags":
            results[key] = playlist_info['tag_list']
        elif key == "tracks":
            results[key] = list(map(lambda x: x['title'], playlist_info['tracks']))
        else:
            logging.error("Unknown playlist metadata key: "+ key)
    return results


def get_additional_playlist_info(playlist_info, client_id):
    additional_playlist_info_url = get_additional_playlist_info_url(playlist_info, client_id)
    logging.info("Requesting additional playlist info from URL: "+ additional_playlist_info_url)
    additional_playlist_info = get_html(additional_playlist_info_url)
    additional_playlist_data = list(filter(lambda x: x['id'] == playlist_info['id'],
                                      additional_playlist_info.json()['collection']))[0]
    logging.info("Got additional playlist info: "+ str(additional_playlist_data))
    return additional_playlist_data


def get_additional_playlist_info_url(playlist_info, client_id):
    base_url = "https://api-v2.soundcloud.com/users/{0}/{1}?representation=mini&client_id={2}&limit=1000"
    if (playlist_info['kind'] == "playlist"):
        return base_url.format(playlist_info['user_id'], "playlists_without_albums", client_id)
    else:
        return base_url.format(playlist_info['user_id'], "albums", client_id)


def get_artist_metadata(metadata, client_id, track_info, artist_path):
    user_id = track_info['user']['id']
    user_info = get_user_metadata(user_id, client_id)
    results = {}
    for key in metadata:
        if key == "albums":
            results[key] = get_user_albums_metdata(user_id, client_id)
        elif key == "comments":
            results[key] = get_user_comments_metadata(user_id, client_id)
        elif key == "description":
            results[key] = user_info['description']
        elif key == "location":
            results[key] = {
                "country": user_info['country'],
                "city": user_info['city']
            }
        elif key == "name":
            results[key] = user_info['full_name']
        elif key == "username":
            results[key] = user_info['username']
        elif key == "followers":
            results[key] = user_info['followers_count']
        elif key == "following":
            results[key] = user_info['followings_count']
        elif key == "likes":
            results[key] = user_info['likes_count']
        elif key == "reposts":
            results[key] = user_info['reposts_count']
        elif key == "user_id":
            results[key] = user_id
        elif key == "status":
            results['pro'] = \
                user_info['subscriptions'] and user_info['subscriptions'][0]['product']['id'] == "creator-pro-unlimited"
        elif key == "profile_picture":
            export_user_avatar(user_info['avatar_url'], artist_path)
        elif key == "header":
            export_header_image(user_info, artist_path)
        elif key == "links":
            results[key] = get_user_links(user_id, client_id)
        elif key == "playlists":
            results[key] = get_user_playlists(user_id, client_id)
        elif key == "spotlight":
            results[key] = get_user_spotlight(user_id, client_id)
        else:
            logger.error("Unknown artist metadata key: " + key)
    return results


def get_user_spotlight(user_id, client_id):
    spotlight_url = "https://api-v2.soundcloud.com/users/{0}/spotlight?" \
                    "client_id={1}&limit={2}".format(user_id, client_id, request_limit)
    logging.info("Requesting user spotlight from URL: "+ spotlight_url)
    spotlight_info = get_html(spotlight_url)
    spotlight_data = list(map(lambda x: x['title'], spotlight_info.json()['collection']))
    logging.info("Got user spotlight data: "+ str(spotlight_data))
    return spotlight_data


def get_user_playlists(user_id, client_id):
    playlists_url = "https://api-v2.soundcloud.com/users/{0}/playlists_without_albums?representation=mini?" \
                    "&client_id={1}&limit={2}".format(user_id, client_id, request_limit)
    logger.info("Requesting playlists metadata from URL: " + playlists_url)
    playlists_info = get_html(playlists_url)
    playlists_data = list(map(lambda x: x['title'], playlists_info.json()['collection']))
    logger.info("Got playlist names: " + str(playlists_data))
    return playlists_data


def get_user_links(user_id, client_id):
    user_links_url = "https://api-v2.soundcloud.com/users/soundcloud:users:{0}/web-profiles?" \
                     "client_id={1}".format(user_id, client_id)
    logger.info("Requesting user links from URL: "+ user_links_url)
    user_links_data = get_html(user_links_url).json()
    logger.info("Got user links: "+ str(user_links_data))
    return user_links_data


def get_header_url(page_html):
    header_url = re.search(r'visual_url":"(.+?)"', page_html).group(1)
    return header_url


def export_header_image(user_info, artist_path):
    user_url = user_info['permalink_url']
    logger.info("Requesting artist html page: "+ user_url)
    user_info = get_html(user_url)
    logger.info("Got artist html page")
    header_url = get_header_url(user_info.text)
    logger.info("Requesting header image from URL: "+ header_url)
    header_data = get_html(header_url)
    export_image(header_data.content, artist_path, "header.jpg")


def export_user_avatar(avatar_url, artist_path):
    logging.info("Requesting user avatar image from url: " + avatar_url)
    avatar_image_info = get_html(avatar_url)
    export_image(avatar_image_info.content, artist_path, "avatar.jpg")
    logging.info("Written user avatar image")


def get_user_metadata(user_id, client_id):
    user_url = "https://api.soundcloud.com/users/{0}?client_id={1}".format(user_id, client_id)
    logger.info("Requesting user metadata from URL: "+ user_url)
    user_info = get_html(user_url)
    user_data = user_info.json()
    logger.info("Got user metadata: "+ str(user_data))
    return user_data


def get_user_albums_metdata(user_id, client_id):
    albums_url = "https://api-v2.soundcloud.com/users/{0}/albums?" \
                 "client_id={1}&limit={2}".format(user_id, client_id, request_limit)
    logger.info("Requesting albums metadata from URL: "+ albums_url)
    albums_info = get_html(albums_url)
    albums_data = list(map(lambda x: x['title'], albums_info.json()['collection']))
    logger.info("Got album names: "+ str(albums_data))
    return albums_data


def get_user_comments_metadata(user_id, client_id):
    comments_url = "https://api-v2.soundcloud.com/users/{0}/comments?" \
                   "client_id={1}&limit={2}".format(user_id, client_id, request_limit)
    logger.info("Requesting comments metadata from URL: "+ comments_url)
    comments_info = get_html(comments_url)
    comments_data = list(map(lambda x: {
        "date": x["created_at"],
        "comment": x["body"],
        "timestamp": x["timestamp"],
        "track_name": x["track"]["title"],
        "track_url": x["track"]["permalink_url"]
    }, comments_info.json()['collection']))
    logger.info("Got comments: "+ str(comments_data))
    return comments_data


def get_track_metadata(metadata, client_id, track_id, track_info, track_path):
    results = {}
    for key in metadata:
        if key == "playlists":
            results[key] = get_track_playlists_metadata(track_id, client_id)
        elif key == "albums":
            results[key] = get_track_albums_metadata(track_id, client_id)
        elif key == "background":
            export_background_image(track_id, track_path)
        elif key == "artist":
            results[key] = track_info['user']['username']
        elif key == "cover_art":
            export_artwork(track_info["artwork_url"], track_path)
        elif key == "date":
            results[key] = track_info['created_at']
        elif key == "description":
            results[key] = track_info['description']
        elif key == "likes":
            results[key] = track_info['likes_count']
        elif key == "listens":
            results[key] = track_info['playback_count']
        elif key == "reposts":
            results[key] = track_info['reposts_count']
        elif key == "tags":
            results[key] = track_info['tag_list']
        elif key == "related_tracks":
            results[key] = get_related_metadata(track_id, client_id)
        elif key == "status":
            results[key] = get_status(track_info)
        elif key == "comments":
            results[key] = get_comments(track_id, client_id)
        else:
            logger.error("Unknown track metadata key: "+ key)
    return results


def get_comments(track_id, client_id):
    comments_url = "https://api-v2.soundcloud.com/tracks/{0}/comments?threaded=1&filter_replies=0&" \
                   "client_id={1}&limit={2}".format(track_id, client_id, request_limit)
    logging.info("Requesting comments metadata from url: "+ comments_url)
    comments_info = get_html(comments_url)
    comments_data = list(map(lambda x: {
        "date": x["created_at"],
        "comment": x["body"],
        "timestamp": x["timestamp"],
        "name": x["user"]["full_name"]
    }, comments_info.json()["collection"]))
    logging.info("Got comments data: "+ str(comments_data))
    return comments_data


def get_status(track_info):
    if track_info['monetization_model'] == "SUB_HIGH_TIER":
        return "GO+"
    else:
        return "free"


def export_artwork(artwork_url, path, filename="artwork"):
    logger.info("Requesting artwork url: " + artwork_url)
    artwork_info = get_html(artwork_url)
    artwork_name, artwork_ext = os.path.splitext(artwork_url)
    artwork_file_name = filename + artwork_ext
    export_image(artwork_info.content, path, artwork_file_name)
    logging.info("Written artwork to file: " + artwork_file_name)


def export_background_image(track_id, track_path, filename="background.jpg"):
    # TODO: Verify the image url by searching for it in the html content
    background_image_url = "https://va.sndcdn.com/bg/soundcloud:tracks:{0}/soundcloud-tracks-{0}.jpg".format(track_id)
    logging.info("Requesting background image from url: "+ background_image_url)
    background_image_info = get_html(background_image_url, fail_on_error=False)
    if background_image_info.status_code != 200:
        logging.info("Background image not found for track")
    else:
        export_image(background_image_info.content, track_path, filename)
        logging.info("Written background image")


def get_track_playlists_metadata(track_id, client_id):
    playlists_url = "https://api-v2.soundcloud.com/tracks/{0}/playlists_without_albums?representation=mini&" \
                    "client_id={1}&limit={2}".format(track_id, client_id, request_limit)
    logging.info("Requesting playlists metadata from url: "+ playlists_url)
    playlists_info = get_html(playlists_url)
    playlist_names = list(map(lambda x: x["title"], playlists_info.json()["collection"]))
    logging.info("Got playlist names: "+ str(playlist_names))
    return playlist_names


def get_track_albums_metadata(track_id, client_id):
    albums_url = "https://api-v2.soundcloud.com/tracks/{0}/albums?representation=mini&" \
                    "client_id={1}&limit={2}".format(track_id, client_id, request_limit)
    logging.info("Requesting albums metadata from url: "+ albums_url)
    albums_info = get_html(albums_url)
    album_names = list(map(lambda x: x["title"], albums_info.json()["collection"]))
    logging.info("Got album names: "+ str(album_names))
    return album_names


def get_related_metadata(track_id, client_id):
    related_url = "https://api-v2.soundcloud.com/tracks/{0}/related?" \
                  "client_id={1}&limit={2}".format(track_id, client_id, request_limit)
    logging.info("Requesting related tracks metadata from url: "+ related_url)
    related_info = get_html(related_url)
    related_names = list(map(lambda x: x["title"], related_info.json()["collection"]))
    logging.info("Got related track names: "+ str(related_names))
    return related_names


def export_image(artwork, track_path, file_name):
    image_file_path = os.path.join(track_path, file_name)
    logger.info("Writing image to file: " + image_file_path)
    with open(image_file_path, "wb") as image_file:
        image_file.write(artwork)


def archive_track(track_id, client_id, custom_artist_fn, track_metadata, artist_metadata, album_name="Singles", base_path=DATA_PATH):
    track_info = get_track_info(track_id, client_id)

    track_name = track_info["title"]
    logger.info("Track name: " + track_name)

    full_track = get_track(track_info, client_id)

    uploader_name = track_info["user"]["username"]
    logger.info(
        "Track uploader was {0}. Press enter to continue or provide an alternative artist name: ".format(uploader_name))

    artist_name = get_artist_name(uploader_name, custom_artist_fn)
    logger.info("Chosen artist name is: " + artist_name)

    artist_path = get_path(base_path, artist_name)

    track_path = get_track_path(artist_path, album_name, track_name)
    logger.info("Track path is: " + track_path)

    export_track(full_track, track_path, "track.mp3")

    if track_metadata == []:
        export_metadata(track_info, track_path, "meta.json")
    else:
        track_metadata1 = get_track_metadata(track_metadata, client_id, track_id, track_info, track_path)
        export_metadata(track_metadata1, track_path, "meta.json")

    if artist_metadata != []:
        artist_metadata1 = get_artist_metadata(artist_metadata, client_id, track_info, artist_path)
        export_metadata(artist_metadata1, artist_path, "meta.json")


logger = logging.getLogger("scdownload")

client_id = "cZQKaMjH39KNADF4y2aeFtVqNSpgoKVj"


def download(url, custom_artist_fn, track_metadata=[], artist_metadata=[], playlist_metadata=[]):
    logger.info("Requesting SoundCloud url: " + url)
    response = get_html(url)

    track_search = re.search(r'soundcloud://sounds:(.+?)"', response.text)
    playlist_search = re.search(r'soundcloud://playlists:(.+?)"', response.text)

    if track_search != None:
        track_id = track_search.group(1)
        logger.info("Found track ID {0} on page. Dowloading track...".format(track_id))
        archive_track(track_id, client_id, custom_artist_fn, track_metadata, artist_metadata)
        return 0
    elif playlist_search != None:
        playlist_id = playlist_search.group(1)
        logger.info("Found playlist ID {0} on page. Downloading playlist...".format(playlist_id))
        playlist_name = get_playlist_name(response.content)
        logger.info("Playlist name: " + playlist_name)
        playlist_info = get_playlist_info(playlist_id, client_id)

        playlist_author_path = get_path(DATA_PATH, playlist_info['user']['permalink'])
        playlist_path = get_path(playlist_author_path, playlist_name)

        for track_info in playlist_info['tracks']:
            archive_track(str(track_info["id"]), client_id, custom_artist_fn, track_metadata, artist_metadata,
                          album_name=playlist_name, base_path=playlist_path)

        playlist_metadata1 = get_playlist_metadata(playlist_metadata, client_id, playlist_info, playlist_path)
        export_metadata(playlist_metadata1, playlist_path, "meta.json")

        return 0
    else:
        logger.error("No valid track or playlist ID found on page. Is this a valid SoundCloud link?")
        return -1


def run_cmdline():
    # url = "https://soundcloud.com/yung-bruh-3/gemstone-bullets-poppin-out-the-tech"
    logger.info("Enter the SoundCloud URL of the track/playlist to download: ")
    soundcloud_url = input()
    result = download(soundcloud_url, input)
    if result < 0:
        sys.exit(result)