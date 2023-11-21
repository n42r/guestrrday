<div align="center">

# guestrrday 

![GitHub License](https://img.shields.io/github/license/n42r/guestrrday)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Static Badge](https://img.shields.io/badge/coverage-89%25-blue)

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

I made this tool because I had to strict requirements: *high prediction rate* and *high accuracy* **at scale**. So what is the current prediction rate and accuracy you ask? Well, there are three variables affecting prediction rate and accuracy: (1) the completeness of the discogs.com database, (2) unsanitized tracknames / filenames, and (3) the limitations of the discogs search engine (relative to duckduckgo or google, for example). We can't control number (1) but we can control (2) & (3), and this is what this tool focuses on. The completeness of the discogs DB and any music DB really varies based on the music: for example, data on  90s electronic music singles is much more complete than pre-war blues releases (1930s, 40s).

To throw rough estimates from experience, I would say the average completness of the discogs DB with regards to the *year of release* is around 85-90%. 95% of those are typically detected by this tool. 

However, it must be noted, there are many singles on discogs which have no original year of release but that of a reissue year, and in that case the tool will return the reissue date. For example, a disco single released in 1970s but for which no year is available for the original release on the discogs DB, but a year is availalbe for a reissue released at a later date (say 2015). In that case, the detected year for that track would be 2015 (and the label would be the reissue label).

## Contribution

Looking forward to find like-minded collaborators passionate about similar subjects. Push requests are very welcome, just create an issue.

## License

This project is Licensed under the [MIT](/LICENSE) License.
