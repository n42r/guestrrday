import click
from guesterday.year_guesser import year_guesser

@click.command()
@click.option('--input', default='.', required=True, help='Input directory with music files in it.')
@click.option('--range', default='1910-2023', help='Range: YYYY-YYYY. Not required, but gives more accurate results [default "1910-2023"].')
def main(input, range):
	"""Toolset for the digital music collector and historian:
		- Get years of tracks in bulk, 
		- Generate a youtube playlist from a tracklisk (forthcoming)
		- And several other tools to come."""
		
	mn, mx = range.split('-')
	dg = year_guesser(int(mn), int(mx))
	dg.guess_by_dir(input)


if __name__ == "__main__":
	main()

