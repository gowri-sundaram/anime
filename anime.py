import argparse
from bs4 import BeautifulSoup
import httplib
import logging
from random import randint
import re
import sys
import urllib2

MIN_ID=1
MAX_ID=11000

class Anime(object):
  id = -1
  title = ""
  arithmeticMean = -1
  weightedMean = -1

  def __init__ (self, id, title, arithmeticMean, weightedMean):
    self.id = id
    self.title = title
    self.arithmeticMean = arithmeticMean
    self.weightedMean = weightedMean

# Returns the Anime object represented by the anime id as per
# Anime News Network (ANN).
# Returns 'None' if:
#   - the entry corresponding to this id does not exist, OR
#   - this id represents a Manga entry, OR
#   - if the anime does not have any associated rating attribute, OR
#   - either the arithmetic or the weighted mean is lower than |threshold|.
def getAnime(animeId, threshold):
  url = "http://www.animenewsnetwork.com/encyclopedia/anime.php?id=%s" % str(animeId)
  try: 
    response = urllib2.urlopen(url)
    html = response.read()
    parsedHtml = BeautifulSoup(html, "lxml")

    title =  parsedHtml.find("div", {"id": "page-title"}).find("h1", {"id": "page_header"}).contents[0]
    # Exclude manga entries.
    if 'manga' in title:
      return None
    
    ratingText =  parsedHtml.find("div", {"id": "ratingbox"})
    # Exclude entries with no ratings.
    if ratingText is None:
      return None

    arithmeticMean = float(re.findall(b'<b>Arithmetic mean:</b> (\d+.\d+)', str(ratingText))[0]);
    weightedMean = float(re.findall(b'<b>Weighted mean:</b> (\d+.\d+)', str(ratingText))[0]);
    # Exclude entries with low ratings.
    if arithmeticMean < threshold or weightedMean < threshold:
      return None

    anime = Anime(animeId, title, arithmeticMean, weightedMean)
    return anime

  except urllib2.HTTPError, e:
    logging.warning('HTTPError = %s, animeId = %s' % (str(e.code), str(animeId)))
  except urllib2.URLError, e:
    logging.warning('URLError = %s, animeId = %s' % (str(e.reason), str(animeId)))
  except httplib.HTTPException, e:
    logging.warning('HTTPException, animeId = %s' % str(animeId))
  except Exception:
    import traceback
    logging.warning('generic exception: ' + traceback.format_exc())
 
# Returns a random Integer between |MIN_ID| and |MAX_ID|, both inclusive.
def getRandomId():
  return randint(MIN_ID, MAX_ID)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--threshold', required=True, type=int, help="Minimum allowed rating as per AnimeNewsNetwork (ANN)")
  args = parser.parse_args()
  print "Threshold: %s" % args.threshold

  visited = set()
  while (True):
    animeId = getRandomId()
    if (animeId in visited):
      continue
    visited.add(animeId)
    anime = getAnime(animeId, args.threshold)
    if anime is None:
      continue
    print str(anime.__dict__)
