import pytest
from pathlib import Path

from guestrrday.track import track		
#from guestrrday.track import tracklist

def test_track_init_correct_clean_title_no_filename():
	t = track('02. Prince - Musicology (Timelife Mix)')
	assert t.get_filename_path() is None \
		and t.get_title() == 'Prince - Musicology (Timelife Mix)' \
		and t.get_artist() == 'Prince' \
		and t.get_song_title() == 'Musicology' \
		and t.get_track() == 2 \
		and t.get_qualifier() == 'Timelife Mix' \
		and t.get_year() == None

def test_track_init_correct_dirty1_fixed_title_no_filename():
	t = track('02. Prince _ Musicology (Timelife Mix)')
	assert t.get_filename_path() is None \
		and t.get_title() == 'Prince - Musicology (Timelife Mix)' \
		and t.get_artist() == 'Prince' \
		and t.get_song_title() == 'Musicology' \
		and t.get_track() == 2 \
		and t.get_qualifier() == 'Timelife Mix' \
		and t.get_year() == None


def test_track_init_correct_dirty2_fixed_title_no_filename():
	t = track('2 Prince  Musicology (Timelife Mix)')
	assert t.get_filename_path() is None \
		and t.get_title() == 'Prince - Musicology (Timelife Mix)' \
		and t.get_artist() == 'Prince' \
		and t.get_song_title() == 'Musicology' \
		and t.get_track() == 2 \
		and t.get_qualifier() == 'Timelife Mix' \
		and t.get_year() == None


def test_track_init_correct_dirty2_fixed_title_no_filename():
	t = track('032. Lydia Lunch ＂Mechanical Flattery＂ 1980')
	assert t.get_filename_path() is None \
		and t.get_title() == 'Lydia Lunch - Mechanical Flattery 1980' \
		and t.get_artist() == 'Lydia Lunch' \
		and t.get_song_title() == 'Mechanical Flattery 1980' \
		and t.get_track() == 32 \
		and t.get_qualifier() == None \
		and t.get_year() == None

def test_track_init_correct_dirty_not_fixed_title_no_filename():
	t = track('032. Lydia Lunch Mechanical Flattery')
	assert t.get_filename_path() is None \
		and t.get_title() == 'Lydia Lunch Mechanical Flattery' \
		and t.get_artist() == 'Lydia Lunch Mechanical Flattery' \
		and t.get_song_title() == 'Lydia Lunch Mechanical Flattery' \
		and t.get_track() == 32 \
		and t.get_qualifier() == None \
		and t.get_year() == None


def test_track_init_correct_filename():
#	MyFolder\MyAlbum\02. Prince - Musicology (Timelife Mix).mp3
	Path('tests/008. The Isley Brothers - Fight the Power, Pts. 1 & 2.m4a').touch()
	t = track('tests/008. The Isley Brothers - Fight the Power, Pts. 1 & 2.m4a')
	assert t.get_filename_path() == 'tests/008. The Isley Brothers - Fight the Power, Pts. 1 & 2.m4a'
	assert t.get_title() == 'The Isley Brothers - Fight the Power, Pts. 1 & 2'
	Path('tests/008. The Isley Brothers - Fight the Power, Pts. 1 & 2.m4a').unlink()

def test_track_init_non_exists_filename():
#	MyFolder\MyAlbum\02. Prince - Musicology (Timelife Mix).mp3
	t = track('tests/008. The Isley Brothers - Fight the Power.m4a')
	assert t.get_filename_path() is None
	assert t.get_title() == 'tests/008. The Isley Brothers - Fight the Power.m4a'



# def test_many_tracks():
	# global TRACK_LIST
	# for i in TRACK_LIST:
		# inp, out  = i
		# tr = track(inp)
		# assert tr.__dict__ == dict(out)
	
