import click
from guestrrday.guestrrday import guess

@click.command()
@click.option('--input', required=True, help='Directory with music files or text file with tracklist, or comma separated list of tracks.')
def main(input):
	"""Tool for guessing the year and record label of music tracks
	
	Args:
		input (str): Directory with music files or text file with tracklist, or comma separated list of tracks. Just give it what you need.
	"""
	return guess(input)


if __name__ == "__main__":
	main()

