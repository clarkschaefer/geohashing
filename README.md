Python implementation of https://xkcd.com/426/, as a first step in learning to use the Python stdlib among other things. Uses the AlphaVantage API to retrieve daily opens, but doesn't handle all times of the day and all times of the week quite right yet. Also, not yet 30W-compliant, although that is coming, and I do intend to make it a complete runnable Django web app for fun at some point, although maybe I'll make that separate project and make this a CLI tool or something. Who knows!

AlphaVantage API keys can be had at https://www.alphavantage.co/support/#api-key, and they need to be placed in a single file named alphavantage_api_key.txt, which is named in the .gitignore. No API-key stealing for you!
