import os
import time
import yaml
import discogs_client

from guestrrday.track import track, tracklist
from guestrrday import utils

D_CLIENT = None


def guess(inp, formats="standard_plus_label"):
    """Entrypoint into the guessing funtionality

    Args:
            in (str): Directory with music files or text file with tracklist,

                    or comma separated list of tracks.

    Returns:
            str: in the case of a comma separated list, and None otherwise

    """
    tl = tracklist(location=inp)
    tl.fill()
    for tr in tl:
        discogs_guess_track(tr)
        new_name = utils.format_output(
            tr.get_full_title(), tr.year, tr.label, form="standard_plus_label"
        )
        tr.set_new_name(new_name)
        print(tr.get_new_name())
    return flush_results(tl)


def discogs_guess_track(trck):
    """Function that queries discogs and searches for the earliest matching hit.

    Args:
            trck (guestrrday.track.track): Track object

    Returns:
            guestrrday.track.track: updates the original track in the args

                    with year and label and returns it (year and label are None in case no year is found).
    """

    title = trck.get_title()

    # first attempt: search for track as a single

    page1 = search_and_get_results(
        title, type="release", formats="Single|12''|10''|7''", sort="year,asc"
    )
    results = convert_discogs_results(page1)
    res1 = utils.get_earliest_matching_hit(results, title)

    # second attempt: singles but drop anything between brackets (mix name typically)

    # from 'Puff Daddy - I love you (Abas remix)' => 'Puff Daddy - I love you'
    title = utils.get_base_title(title)

    page1 = search_and_get_results(
        title, type="release", formats="Single|12''|10''|7''", sort="year,asc"
    )
    results = convert_discogs_results(page1)
    res2 = utils.get_earliest_matching_hit(results, title)

    # third attempt: any 'kind' of release (albums, compilations). Plus no mix name

    title = utils.get_base_title(title)

    page1 = search_and_get_results(title, type="release", formats="", sort="year,asc")
    results = convert_discogs_results(page1)
    res3 = utils.get_earliest_matching_hit(results, title, single=False)

    ls = [i for i in [res1, res2, res3] if i is not None]
    if len(ls) > 0:
        mn = min(ls, key=lambda t: t[0])
        trck.year = mn[0]
        trck.label = mn[1]
    return trck


def flush_results(tl):
    """Flush out results: print in a file, rename files in a dir, or return comma separated list.

    Args:
            tl (guestrrday.track.tracklist): Tracklist object that contains guessed information.

    Returns:
            str: in the case of a comma separated list, and None otherwise

    """
    if tl.type == "dir":
        rename_tracks(tl)
    elif tl.type == "file":
        writeout_tracklist(tl)
    #else:
    #    print(', '.join([tr.get_new_name() for tr in tl]))


def rename_tracks(tl):
    """Rename music files based on guessed dates / labels.

    Args:
            tl (guestrrday.track.tracklist): Tracklist object that contains guessed information.

    Returns:
            None
    """

    for tr in tl:
        if tr.year is not None:
            utils.rename(tr)


def writeout_tracklist(tl):
    """Write out a file with each track in the original including a guessed date / label.

    Args:
            tl (guestrrday.track.tracklist): Tracklist object that contains guessed information.

    Returns:
            None
    """
    ext = tl.location[tl.location.rfind(".") :]
    base_name = tl.location[: tl.location.rfind(".")]
    if "." not in tl.location:
        ext = ""
        base_name = tl.location
    outfile = f"{base_name}-guessed.{ext}"
    out = [tr.get_new_name() for tr in tl]
    with open(outfile, "w", encoding="utf8") as f:
        f.write("\n".join(out))
    f.close()


def search_and_get_results(title, formats, type, sort, first=True):
    """Function to query the discogs API and manage throttling and returning a list of results.

    Args:
            title (str): The track title and artist name
            formats (str): The formats of the medium to search for. Values used here are:
                    - "Single|12''|10''|7''": search for singles only
                    - "": no restriction on formats (i.e. all)
            type (str): The type of entities to consider. The one used here is "release".
                    Other options on discogs are "artist", "label", etc
            sort (str): Sorting order and condition. The value used here is "year,asc"
            first (bool): Flag used for managing API throttling. Don't modify!

    Returns:
            list: list of objects that contains attributes as well as a dict called data

                    which includes most of the info (see convert_discogs_results below)
    """

    time.sleep(1)
    global D_CLIENT

    if D_CLIENT is None:
        D_CLIENT = discogs_client.Client(
            "ExampleApplication/0.1", user_token=load_config()
        )
    page1 = None
    results = D_CLIENT.search(title, type=type, format=formats, sort=sort)
    try:
        page1 = results.page(1)
    except discogs_client.exceptions.HTTPError as e:
        print(e)
        time.sleep(60)
        return search_and_get_results(title, formats, type, sort, first=False)
    return page1


def load_config():
    """Function to load the config file and read the discogs user token.

    Args:
            None
    Returns:
            str: discogs_user_token
    """

    con = None
    if os.path.isfile(".\\guestrrday\\config.yaml"):
        with open(".\\guestrrday\\config.yaml", "r", encoding="utf-8") as stream:
            try:
                con = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    if con is None:
        raise Exception("No 'config.yaml' found or is empty.")

    if con.get("discogs_user_token") is None:
        raise Exception("You must provide a discogs_user_token in 'config.yaml'.")
    return con.get("discogs_user_token")


def convert_discogs_results(page):
    """Convert discogs heterogenous pythonic results into a simple homogenous dict

    Args:
            list (obj): results returned by the discogs_client

    Returns:
            dict: contaning the year, title, and label of each hit
    """

    res = []
    for i in page:
        item = {}
        if i is None:
            continue
        item["year"] = i.data.get("year")
        item["title"] = i.title
        item["label"] = i.data.get("label")[0]
        res.append(item)
    return res
