import pytest
import shutil
from pathlib import Path
	
from guestrrday.guestrrday import year_guesser
from guestrrday.track import track

def test_guess_all_succeed():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	out = (1980, 'Derby')
	Path('tests/temp/003. Skyy - High.m4a').touch()
	tr = track('tests/temp/003. Skyy - High.m4a')
	out2 = (1999, 'MCA Records')
	Path('tests/temp/028. The Roots - The Next Movement.m4a').touch()
	tr2 = track('tests/temp/028. The Roots - The Next Movement.m4a')
	
	assert dg.guess_track(tr) == out
	assert dg.guess_track(tr2) == out2
	shutil.rmtree('tests/temp/')
	

def test_guess_all_fail():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	inp = 'tests/temp/019. Bill Connors Trio A Pedal 1985.m4a'
	Path(inp).touch()
	tr = track(inp)
	in2 = "tests/temp/096. Left Hand Frank and his Blues Band, Blues won't let me be"
	Path(in2).touch()
	tr2 = track(in2)
	
	assert dg.guess_track(tr) is None
	assert dg.guess_track(tr2) is None
	shutil.rmtree('tests/temp/')
	
def test_guess_directory_all_succeed():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	in1 = 'tests/temp/003. Skyy - High.m4a'
	out = 'tests/temp/003. Skyy - High (Derby, 1980).m4a'
	Path(in1).touch()
	in2 = 'tests/temp/028. The Roots - The Next Movement.m4a'
	out2 = 'tests/temp/028. The Roots - The Next Movement (MCA Records, 1999).m4a'
	Path(in2).touch()
	dg.guess_by_dir('tests/temp/')
	
	assert Path(out).exists()
	assert Path(out2).exists()
	shutil.rmtree('tests/temp/')


def test_guess_directory_all_fail():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	in1 = 'tests/temp/019. Bill Connors Trio A Pedal 1985.m4a'
	out = 'tests/temp/019. Bill Connors Trio A Pedal 1985.m4a'
	Path(in1).touch()
	in2 = "tests/temp/096. Left Hand Frank and his Blues Band, Blues won't let me be"
	out2 = "tests/temp/096. Left Hand Frank and his Blues Band, Blues won't let me be"
	Path(in2).touch()
	dg.guess_by_dir('tests/temp/')
	
	assert Path(out).exists() 
	assert Path(out2).exists()
	shutil.rmtree('tests/temp/')


def test_guess_tracklist_all_succeed():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	in1 = 'tests/temp/tracklist'
	#Path(in1).touch()	
	with open(in1, 'w', encoding='utf8') as f:
		f.write('tests/temp/003. Skyy - High.m4a\n')
		f.write('tests/temp/028. The Roots - The Next Movement.m4a\n')
	f.close()
	
	out1= in1 + '-guessed'
	lines_out = ['tests/temp/003. Skyy - High (Derby, 1980).m4a', 'tests/temp/028. The Roots - The Next Movement (MCA Records, 1999).m4a']
	
	dg.guess_by_tracklist(in1)

	idx = 0
	with open(out1, encoding='utf8') as f:
		for line in f:
			assert line.strip() == line_out[idx].strip()
			idx += 1
	shutil.rmtree('tests/temp/')



def test_guess_tracklist_all_fail():
	dg = year_guesser()
	Path('tests/temp/').mkdir()
	in1 = 'tests/temp/tracklist'
	#Path(in1).touch()	
	with open(in1, 'w', encoding='utf8') as f:
		f.write('tests/temp/019. Bill Connors Trio A Pedal 1985.m4a\n')
		f.write("tests/temp/096. Left Hand Frank and his Blues Band, Blues won't let me be\n")
	f.close()
	
	out1= in1 + '-guessed'
	lines_out = ['tests/temp/019. Bill Connors Trio A Pedal 1985.m4a', "tests/temp/096. Left Hand Frank and his Blues Band, Blues won't let me be.m4a"]
	
	dg.guess_by_tracklist(in1)

	idx = 0
	with open(out1, encoding='utf8') as f:
		for line in f:
			assert line.strip() == line_out[idx].strip()
			idx += 1
	shutil.rmtree('tests/temp/')
	

# def test_many_tracks():
	# dg = year_guesser()
	# global GUESS_LIST
	# for i in GUESS_LIST:
		# inp, out  = i
		# tr = track(inp)
		# assert dg.guess_track(tr) == out
		
