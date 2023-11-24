import pytest
import os.path
import shutil
from pathlib import Path
	
from guestrrday.guestrrday import guess
from guestrrday.track import track

@pytest.fixture(autouse=True)
def test_clean_up_in_case_prev_fail():
	shutil.rmtree('tests/temp-test-files/', ignore_errors=True)
	yield
	shutil.rmtree('tests/temp-test-files/',ignore_errors=True)


def gen(title, guess):
	dir = os.path.dirname(title)
	base = os.path.basename(title)
	base = base[ : base.rfind('.') ]
	ext = title[ title.rfind('.') + 1 : ]
	return os.path.join(dir, f'{base} {guess}.{ext}')

def test_guess_all_succeed():
	Path('tests/temp-test-files/').mkdir()
	item1 = 'tests/temp-test-files/003. Skyy - High.m4a'
	Path(item1).touch()
	out = '(Derby, 1980)'
	out = gen(item1, out)
	tr = track(item1)
	item2 = 'tests/temp-test-files/028. The Roots - The Next Movement.m4a'
	Path(item2).touch()
	out2 = '(MCA Records, 1999)'
	out2 = gen(item2, out2)
	tr2 = track(item2)
	guess('tests/temp-test-files/')
	
	assert Path(out).exists()
	assert Path(out2).exists()
	
	shutil.rmtree('tests/temp-test-files/')
	

def test_guess_all_fail():
	Path('tests/temp-test-files/').mkdir()
	inp = 'tests/temp-test-files/019. Bill Connors Trio A Pedal 1985.m4a'
	Path(inp).touch()
	tr = track(inp)
	in2 = "tests/temp-test-files/066. BIGTOWN PLAYBOY LEddie Taylor.m4a"
	Path(in2).touch()
	tr2 = track(in2)
	
	guess('tests/temp-test-files/')
	
	assert Path(inp).exists()
	assert Path(in2).exists()

	shutil.rmtree('tests/temp-test-files/')
	
def test_guess_directory_all_succeed():
	Path('tests/temp-test-files/').mkdir()
	in1 = 'tests/temp-test-files/003. Skyy - High.m4a'
	out = '(Derby, 1980)'
	out = gen(in1, out)
	Path(in1).touch()
	in2 = 'tests/temp-test-files/028. The Roots - The Next Movement.m4a'
	out2 = '(MCA Records, 1999)'
	out2 = gen(in2, out2)
	Path(in2).touch()
	
	guess('tests/temp-test-files/')
	
	assert Path(out).exists()
	assert Path(out2).exists()
	shutil.rmtree('tests/temp-test-files/')


def test_guess_tracklist_all_succeed():
	Path('tests/temp-test-files/').mkdir()
	in1 = 'tests/temp-test-files/tracklist'
	with open(in1, 'w', encoding='utf8') as f:
		f.write('003. Skyy - High\n')
		f.write('028. The Roots - The Next Movement\n')
	f.close()
	
	out1= in1 + '-guessed'
	lines_out = ['003. Skyy - High (Derby, 1980)', '028. The Roots - The Next Movement (MCA Records, 1999)']
	
	guess(in1)
	
	idx = 0
	with open(out1, encoding='utf8') as f:
		for line in f:
			assert line.strip() == lines_out[idx].strip()
			idx += 1
	shutil.rmtree('tests/temp-test-files/')



def test_guess_tracklist_all_fail():
	Path('tests/temp-test-files/').mkdir()
	in1 = 'tests/temp-test-files/tracklist'
	with open(in1, 'w', encoding='utf8') as f:
		f.write('019. Bill Connors Trio A Pedal 1985\n')
		f.write("066. BIGTOWN PLAYBOY LEddie Taylor\n")
	f.close()
	
	out1= in1 + '-guessed'
	lines_out = ['019. Bill Connors Trio A Pedal 1985', "066. BIGTOWN PLAYBOY LEddie Taylor"]
	
	guess(in1)

	idx = 0
	with open(out1, encoding='utf8') as f:
		for line in f:
			assert line.strip() == lines_out[idx].strip()
			idx += 1
	shutil.rmtree('tests/temp-test-files/')

	
