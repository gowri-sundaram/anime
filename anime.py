import argparse
from bs4 import BeautifulSoup
import httplib
import logging
import os
from random import randint
import re
import urllib2

MIN_ID=1
MAX_ID=11000

class Anime(object):

  def __init__ (self, id, title, arithmeticMean=None, weightedMean=None):
    self.id = id
    self.title = title
    self.arithmeticMean = arithmeticMean
    self.weightedMean = weightedMean

  def isManga(self):
    return "manga" in self.title

  def isOneshot(self):
    return bool(re.findall(b'(OAV)|(movie)|(special)', self.title))

  def isPopular(self, threshold):
    if not self.arithmeticMean or not self.weightedMean:
      return False
    return self.arithmeticMean >= threshold and self.weightedMean >= threshold

# Returns the Anime object represented by the anime id as per
# Anime News Network (ANN).
def getAnime(animeId):
  url = "http://www.animenewsnetwork.com/encyclopedia/anime.php?id=%s" % str(animeId)
  try: 
    response = urllib2.urlopen(url)
    html = response.read()
    parsedHtml = BeautifulSoup(html, "lxml")

    title =  parsedHtml.find("div", {"id": "page-title"}).find("h1", {"id": "page_header"}).contents[0]
    ratingText =  parsedHtml.find("div", {"id": "ratingbox"})

    # Check if rating is specified.
    if ratingText is None:
      return Anime(id=animeId, title=title)
    arithmeticMean = float(re.findall(b'<b>Arithmetic mean:</b> (\d+.\d+)', str(ratingText))[0]);
    weightedMean = float(re.findall(b'<b>Weighted mean:</b> (\d+.\d+)', str(ratingText))[0]);
    return Anime(animeId, title, arithmeticMean, weightedMean)

  except urllib2.HTTPError, e:
    logging.warning('HTTPError=%s, animeId=%s' % (str(e.code), str(animeId)))
  except urllib2.URLError, e:
    logging.warning('URLError=%s, animeId=%s' % (str(e.reason), str(animeId)))
  except httplib.HTTPException, e:
    logging.warning('HTTPException, animeId=%s' % str(animeId))
  except Exception:
    import traceback
    logging.warning('generic exception: ' + traceback.format_exc())

# Returns a random Integer between |MIN_ID| and |MAX_ID|, both inclusive.
def getRandomId():
  return randint(MIN_ID, MAX_ID)

# Reads and returns a set of all lines in |filePath|.
def readToSet(filePath):
  result = set()
  if (os.path.isfile(filePath)):
    handle = open(filePath)
    for animeId in handle.read().splitlines():
      result.add(animeId)
  return result

# Writes all entries in |iterable| to |filePath|.
def writeToFile(iterable, filePath):
  with open(filePath, 'wb') as handle:
    for entry in iterable:
      handle.write(str(entry) + "\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--threshold', type=int, required=True,
      help="Minimum allowed rating as per AnimeNewsNetwork (ANN)")
  parser.add_argument('--limit', type=int, default=10,
      help="Maximum number of recommendations. Default: 10")
  parser.add_argument('--include_oneshots', dest='oneshots', action='store_true', default=False,
      help='Whether to include movie titles, OAVs and special episodes in the results. Default: false')
  parser.add_argument('--dir', default=os.path.dirname(os.path.abspath(__file__)),
      help='Root directory to store excluded anime ids.')

  args = parser.parse_args()
  print("Threshold: %s" % args.threshold)
  print("Limit: %s" % args.limit)
  print("Include one shots: %s" % args.oneshots)
  print("Root directory: %s" % args.dir)

  mangaExcludes = readToSet(os.path.join(args.dir, "manga_ids.txt"))
  invalidExcludes = readToSet(os.path.join(args.dir, "invalid_ids.txt"))
  oneshotExcludes = readToSet(os.path.join(args.dir, "oneshot_ids.txt"))
  visited = set()
  result = []
  count=0
  while (count<args.limit):
    animeId = getRandomId()
    if (animeId in mangaExcludes or animeId in invalidExcludes or animeId in visited):
      continue
    if (not args.oneshots and animeId in oneshotExcludes):
      continue

    anime = getAnime(animeId)
    # Filter out invalid anime ids.
    if anime is None:
      invalidExcludes.add(animeId)
      logging.warning('Anime not found, id=%s' % animeId)
      continue
    # Filter out manga entries.
    if anime.isManga(): 
      mangaExcludes.add(animeId)
      logging.warning('Excluding manga, title=%s' % anime.title)
      continue
    # Filter out oneshot entries, if required.
    if anime.isOneshot():
      oneshotExcludes.add(animeId)
      if not args.oneshots:
        logging.warning('Excluding oneshot, title=%s' % anime.title)
        continue
    # Filter out entries with a low rating.
    if not anime.isPopular(args.threshold):
      visited.add(animeId)
      logging.warning('Excluding unpopular anime, title=%s' % anime.title)
      continue
    print str(anime.__dict__)
    visited.add(animeId)
    result.append(anime)
    count+=1

  print("......................................................");
  print("               ***SUGGESTIONS ***");
  print("......................................................");
  for anime in result:
    print str(anime.__dict__)

  # Write ids back to respective files.
  writeToFile(mangaExcludes, os.path.join(args.dir, "manga_ids.txt"))
  writeToFile(invalidExcludes, os.path.join(args.dir, "invalid_ids.txt"))
  writeToFile(oneshotExcludes, os.path.join(args.dir, "oneshot_ids.txt"))
