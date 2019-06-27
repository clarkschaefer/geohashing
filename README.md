Python implementation of https://xkcd.com/426/, as a first step in learning to use the Python stdlib among other things. Uses the AlphaVantage API to retrieve daily opens, but doesn't handle all times of the day and all times of the week quite right yet. Also, not yet 30W-compliant, although that is coming, and I do intend to make it a complete runnable Django web app for fun at some point, although maybe I'll make that separate project and make this a CLI tool or something. Who knows!

AlphaVantage API keys can be had at https://www.alphavantage.co/support/#api-key, and they need to be placed in a single file named alphavantage_api_key.txt, which is named in the .gitignore. No API-key stealing for you!

Right now the installation process is pretty quick:

git clone
pip install -r requirements.txt
and then go find an alphavantage key and put it in alphavantage_api_key.txt
./geohash.py

And it should spit coordinates out at you for your graticule. It doesn't do any of the things a fully compliant CLI tool might do, and the source I'm using for DJI open data appears to be slightly off from the more commonly accepted geo.crox.net source. A script for the semi-automated retrieval of these API keys is on the todo list, but that will probably come after I split out the different APIs in various submodules to make everything a little more organized. I'm also learning how underscores and the semi-private function system works in Python (among like a billion other things) and those will get implemented in time if they aren't already.
