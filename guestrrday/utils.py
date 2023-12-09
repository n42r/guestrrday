import os
import re
import string
import unidecode
import pkgutil

STOPWORDS = pkgutil.get_data(__name__, "stopwords").decode('utf-8')

def has_music_ext(fn):
    """Check if a filename has a music related extension.

    Args:
            fn (str): filename

    Returns:
            bool: True if has a music extension and False otherwise
    """

    ext_idx = fn.rfind(".")
    if ext_idx > -1:
        ext = fn[ext_idx + 1 :]
        # f_char = ext[0]
        audio_ext_list = [
            "mp3",
            "flac",
            "m4a",
            "ogg",
            "opus",
            "wav",
            "wma",
            "aif",
            "aiff",
        ]
        if ext in audio_ext_list:
            return True
    return False


def get_base_title(title):
    """Given a full title of a song, drop string between brackets (usually mix name)

    Example:
            Puff Daddy - I will always love you (Abas remix)' => 'Puff Daddy - I will always love you'

    Args:
            title (str): The full song title

    Returns:
            str: The stripped song title
    """

    dash_idx = title.find(" - ")
    idx = title.find("[", dash_idx)
    if idx > -1:
        title = title[0:idx]
    idx = title.find("(", dash_idx)
    if idx > -1:
        title = title[0:idx]
    tsplit = title.split(" - ")
    if len(tsplit) == 2:
        [artist, tit] = tsplit
        artist = artist.replace(",", " & ")
        artist = artist.replace(";", " & ")
        artist = artist.replace(" with ", " & ")
        temp_artist = artist.split("&")[0].strip()

        if len(temp_artist.split(" ")) > 1:
            artist = temp_artist
        title = artist + " - " + tit
    return title


def remove_blacklist_chars(fn):
    """Sanitise strings that will be used as filenames on the OS

    Args:
            fn (str): The unsanitised filename

    Returns:
            str: The sanitised filename
    """
    os_blacklist = '\\/:*?"<>|'
    fn = fn.replace('"', "'")
    return "".join([letter for letter in fn if letter not in os_blacklist])


def filter_out_stopwords_punc(lst):
    """Sanitize text for search be removing common english stopwords as well as punctuation

    Args:
            lst (list): A list of words, resulting fron a string split() by spaces

    Returns:
            list: A subset of the args with stopwords and punc elements removed
    """
    return [
        word
        for word in lst
        if not (
            word in STOPWORDS
            or word in string.punctuation
            or len(word) < 2
        )
    ]


def remove_accents(lst):
    """Simplify accented letters to the base letters used in english
    Args:
            lst (list): A list of words, resulting fron a string split() by spaces

    Returns:
            list: The list of words with all accents removes
    """
    return [unidecode.unidecode(word) for word in lst]


def replace_symbols_with_spaces(text):
    """Another search aid, remove symbols from search text
    Args:
            text (str): Pre-Search text

    Returns:
            str: Text with all symbols removed
    """
    text = re.sub(r"[^\w^\-]", " ", text)
    text = re.sub(r"[\W\s][\d\-]+[\W\s]", " ", text)
    dashed = re.findall(r"\w+\-\w+", text)

    dashed = " ".join(dashed)
    dashed = re.sub(r"\-", " ", dashed)
    text = text + " " + dashed
    text = re.sub(" +", " ", text)
    return text


def two_in(st1, st2, limit=2):
    """Atleast [limit] number of text tokens in st1 occur in st2

    Args:
            st1 (str): The source string
            st2 (st2): The destination string
            limit (int): Min num of tokens in st1 to be found in st2. Default is 2, hence func name

    Returns:
            bool: True if condition of function is met, and False otherwise
    """
    st1 = replace_symbols_with_spaces(st1.lower().strip())
    st2 = replace_symbols_with_spaces(st2.lower().strip())

    st1_words = filter_out_stopwords_punc(st1.split(" "))
    st2_words = filter_out_stopwords_punc(st2.split(" "))

    if len(st1_words) == 0 or len(st2_words) == 0:
        st1_words = st1
        st2_words = st2

    st1_words = remove_accents(st1_words)
    st2_words = remove_accents(st2_words)

    limit = min(len(st1_words), len(st2_words), limit)

    intersection = len(set(st1_words) & set(st2_words))

    return intersection >= limit


def get_earliest_matching_hit(hits, title, top_hits=10, google_res=False, single=True):
    """Select the matching hit with the earliest release data in the result set hits

    The earliest because many music usually get reissued on a later date.
    Whenever possible we would like to avoid reissue dates since

    they are typically far from the original release date.

    Args:
            hits (list): List of dicts including results
            title (str): The original search term
            top_hits (int): Number of hits to look into before returning a result (default 10)
            google_res (bool): Used in an earlier version of this tool, feature currently frozen
            single (bool): Important flag because in case of a single we have to match the

                    artist and title, but otherwise we try to do a simpler and less constraning match.

                    See guestrrday.discogs_guess_track function for more info.

    Returns:
            tuple: (x, y) where x is the year and y is the label. If not found, tuple is None
    """
    num_of_words_to_accept = 1
    if single:
        num_of_words_to_accept = 4

    hits = [h for h in hits if h is not None and h.get("year") is not None]
    hits = hits[0 : top_hits - 1]
    hits.sort(key=lambda i: int(i.get("year")))

    for h in hits:
        if two_in(title, h.get("title"), num_of_words_to_accept):
            lbl = h.get("label")
            if lbl is not None:
                words = lbl.split()[:3]
                lbl = " ".join(words)
            yr = int(h.get("year"))
            return (yr, lbl)

    return None


def format_output(title, yr=None, label=None, form="standard_plus_label"):
    """Given a year, label, form, and song title create a new title with the year & label.

    Args:
            title (str): The original full song title.
            yr (int): The guessed year
            lable (str): The guessed record label
            form (str): Enum of three different formats.

                    - "standard_plus_label" (default) appends (year, label) to the end of the song title,
                    - "standard" drops the label, and
                    - [anything else] uses a the format: "YYYY -- title {label}"

    Returns:
            str: The formated name
    """
    if yr is None or yr == -1:
        return title
    new_title = ""
    if form == "standard_plus_label" and label is None:
        form = "standard"
    if form == "standard_plus_label":
        new_title = f"{title} ({label}, {yr})"
    elif form == "standard":
        new_title = f"{title} ({yr})"
    else:
        # the guesterday chronological format
        new_title = f"{yr} -- {title} {{{label}}}"
    return new_title


def rename(tr):
    """Rename a track. New original and new names are encapsulated in tr object.

    Args:
            tr (guestrrday.track.track): And object encapsulating information about a track,

                    which includes its original filename and its new filename already.

    Returns:
            str: The new name if year was found, else the old name unchanged.
    """
    old_fn = tr.filename_path
    new_fn = tr.new_title
    path = "."
    if new_fn is not None and old_fn is not None and old_fn != new_fn:
        try:
            os.rename(old_fn, new_fn)
        except OSError:
            path = os.path.dirname(new_fn)
            new_fn = remove_blacklist_chars(os.path.basename(new_fn))
            try:
                os.rename(old_fn, os.path.join(path, new_fn))
            except OSError as e2:
                print(e2)
                return None
        return os.path.join(path, new_fn)
    return old_fn
