#!/bin/zsh
./geohash.py -d 2019-06-23 -l 47 -122 --dji-open 19999.999
# Should yield fractions [0.21693, 0.72709]
# If it didn't, you beansed something.
