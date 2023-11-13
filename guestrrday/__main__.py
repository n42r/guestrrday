import click
from guestrrday.year_guesser import year_guesser

@click.command()
@click.option('--input', default='.', required=True, help='Input directory with music files in it.')
def main(input):
	"""Toolset for the digital music collector and historian:
		- Get years of tracks in bulk, 
		- Generate a youtube playlist from a tracklisk (forthcoming)
		- And several other tools to come."""
	
	dg = year_guesser()
	dg.guess_by_dir(input)


if __name__ == "__main__":
	main()

