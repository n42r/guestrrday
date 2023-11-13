import click
from guestrrday.guestrrday import year_guesser

@click.command()
@click.option('--input', required=True, help='Input directory with music files or text file with tracklist.')
def main(input):
	"""Toolset for the digital music collector and historian:
		- Get years of tracks in bulk, 
		- Generate a youtube playlist from a tracklisk (forthcoming)
		- And several other tools to come."""
	
	dg = year_guesser()
	dg.guess(input)


if __name__ == "__main__":
	main()

