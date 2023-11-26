<div align="center">

# guestrrday 

#### because for music heads, context matters!

A CLI tool that does one thing and does it well: guess the release date and record label of a set of music tracks. 20,000+ songs guessed so far!

</div>

## Description

The pop music historian's dream: given a directory of music tracks or a list of one or more song names (in a textfile or CLI args), guess the **year of release** and the **record label** of each track.

Example:

```Ike & Tina Turner - A Love Like Yours (Don't Come Knocking Everyday)``` 

**=>** 

```Ike & Tina Turner - A Love Like Yours (Don't Come Knocking Everyday) (London American, 1966)```

The script queries discogs.com and includes some tweaks to increase the precision and accuracy of the search (see [Why This Tool?](#why-this-tool) below).

The tool will rename files if the input is a directory, and will create a new textfile in the case of file, and will print to stdout in case of cli args.


## Installation
  - *guesterrday* can be installed by running `pip install guestrrday`.
  - To update *guesterrday* run `pip install --upgrade guestrrday`.

  > On some systems you might have to change `pip` to `pip3`.


## Usage

General Usage:
```sh
guestrrday --input SOURCE
```

Where _SOURCE_ can be any of: 
- ```Directory``` containing music files, or
- ```Filename``` for a text file containing a list song names, one per line, or
- ```"[song1] [, song2 ] [...]"```: Comma-separated list of song names

The tool will automatically detect which one you mean.

You can run _guestrrday_ as a package if running it as a script doesn't work:
```sh
python -m guestrrday --input SOURCE
```


## Why This Tool?

*TLDR*; The devil in the detail

Guestrrday scans a list of song titles and queries discogs.com for the year and label of each. This is clearly a simple function, right? Why a whole tool?

I made this tool because I had two strict requirements: *high prediction rate* and *accuracy* **at scale**. So what is the current prediction rate and accuracy you ask? Well, there are three variables affecting prediction rate and accuracy: (1) the completeness of the discogs.com database, (2) unsanitized tracknames / filenames, and (3) the limitations of the discogs search engine (ex., sensitivity to slight changes in search terms). We can't control (1) but we can control (2) & (3), and this is what this tool focuses on[^1]. The completeness of the discogs DB and any music DB really varies based on the music: for example, data on 90s electronic music singles is much more complete than pre-war blues releases (1930s, 40s).

To throw rough estimates from experience, I would say the average completness of the discogs DB with regards to the *year of release* is around 85-90%. 95% of those are typically detected by this tool, which gives it a 95% prediction rate.

However, it must be noted, there are many singles on discogs which have no original year of release, in that case the tool will return the year of release of the earliest available reissue. For example, a disco single released in 1970s but for which no year is available for the original release, but a reissue exists (say, one released in 2015), the detected year for that track would be 2015 (and the label would be the reissue label).


## Contribution

Push requests are welcome, just create an issue.

## License

This project is Licensed under the [MIT](/LICENSE) License.


[^1]: I tried generic fuzzy matching ([thefuzz](https://github.com/seatgeek/thefuzz)) but couldn't seem to get as good of an accuracy in search results: I got more false positives and couldn't find a sweetspot in the numerical score to optimize false negatives. Ofcourse I could  have run a large test sets and optimized for that value and fuzzy matching algorithm, but for such a small project it was not worth it.
