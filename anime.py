#region Dependencies
import argparse
from bs4 import BeautifulSoup
import httplib
import logging
import os
from random import randint
import re
import urllib2
#endregion Dependencies

#region Defines
MIN_ID=1
MAX_ID=11000
MAX_RECOMMENDATIONS = 3
#endregion Defines

################################################################################
## anime.py
##
## Console application will take very anime arguments and recommend up to 3
## very anime recommendations. Uses ANN database.
################################################################################

# Stores the meat of the anime
class Anime(object):
    def __init__ (self, id, title, arithmeticMean=None, weightedMean=None):
        self.id = id
        self.title = title
        self.arithmeticMean = arithmeticMean
        self.weightedMean = weightedMean

    def isManga(self):
        return bool (re.findall (b'(manga)', self.title))
    def isTV(self):
        return bool (re.findall (b'(TV)|(special)', self.title))
    def isOVA(self):
        return bool (re.findall (b'(OVA)', self.title))
    def isMovie(self):
        return bool (re.findall (b'(movie)', self.title))

    def isPopular(self, threshold):
        if not self.arithmeticMean or not self.weightedMean:
            return False
        return self.arithmeticMean >= threshold and self.weightedMean >= threshold

# Returns the Anime object represented by the anime id as per
# Anime News Network (ANN).
def getAnime(animeId):
  url = "http://www.animenewsnetwork.com/encyclopedia/anime.php?id=%s" % str(animeId)
  try: 
    # Follow URL
    response = urllib2.urlopen(url)
    # Get HTML page data
    html = response.read()
    # Spruce up the soup
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
def getRandomID():
  return randint(MIN_ID, MAX_ID)

############################ MAIN IS RIGHT HERE ################################
#region Main

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=int, required=True,
                    help="Minimum allowed rating as per AnimeNewsNetwork (ANN)")
parser.add_argument ('--exclude_manga', dest='manga', action='store_false', default=True,
                      help='Remove manga from the recommendations')
parser.add_argument ('--exclude_TV', dest = 'TV', action = 'store_false', default = True,
                     help = "Remove TV anime (including specials) from the recommendations")
parser.add_argument ('--exclude_OVA', dest = 'OVA', action = 'store_false', default = True,
                     help = "Remove OVAs from the recommendations")
parser.add_argument ('--exclude_movie', dest = 'movie', action = 'store_false', default = True,
                     help = "Remove movies from the recommendations")

args = parser.parse_args(['--threshold', '4', '--exclude_TV'])

print ('===========SETTINGS===========')
print ('Minimum Rating:   %s' % args.threshold)
print ('Include Manga:    %s' % args.manga)
print ('Include TV Shows: %s' % args.TV)
print ('Include OVAs:     %s' % args.OVA)
print ('Include movies:   %s' % args.movie)

# The animes
animes = list()
# Loop var
count = 0
# Stores used ANN IDs
usedID = list()
# Flag for getting IDs
getID = True

print ("\n===SEARCHING FOR THE ANIMES===")

# Loop while under the requested amount of recommendations
while (count < MAX_RECOMMENDATIONS):
    # Get an ANN ID
    while (getID):
        # Get random ANN ID 
        animeId = getRandomID() 

        # Check that you didn't already get that ID
        for ID in usedID:
            # Found an old ID; go back and get a new ID
            if (animeId == ID):
                break

        # Did not find any old ID matches
        getID = False
    
    # Save our ID in oldID since it's gonna be used
    usedID.append(animeId)

    # Get very anime information from ANN
    anime = getAnime(animeId)

    # There is no ANN entry with the given ID; 
    if anime is None:
        # Log ID in usedID and try again
        usedID.append(animeId)
        getID = True
    # If new ID is not requested
    if (not getID):
        # If the ID pointed to a manga
        if anime.isManga():
            # Check if user is ok with manga
            if not args.manga:
                # User is not ok; Log ID in usedID and try again
                usedID.append (animeId)
                getID = True
    # If new ID is not requested
    if (not getID):
        # If the ID pointed to a TV series
        if anime.isTV():
            # Check if user is ok with TV series
            if not args.TV:
                # User is not ok; Log ID in usedID and try again
                usedID.append (animeId)
                getID = True
    # If new ID is not requested
    if (not getID):
        # If the ID pointed to a OVAs
        if anime.isOVA():
            # Check if user is ok with OVAs
            if not args.OVA:
                # User is not ok; Log ID in usedID and try again
                usedID.append (animeId)
                getID = True
    # If new ID is not requested
    if (not getID):
        # If the ID pointed to a movie
        if anime.isMovie():
            # Check if user is ok with movies
            if not args.movie:
                # User is not ok; Log ID in usedID and try again
                usedID.append (animeId)
                getID = True
    # If new ID is not requested
    if (not getID):
         # If the ID pointed to an item below threshold
        if not anime.isPopular(args.threshold):
            # Log ID in usedID and try again
            usedID.append (animeId)
            getID = True
    # Only increment if there was no premature new ID request
    if (not getID):
        print ("FOUND [%d of %d]" % (count + 1, MAX_RECOMMENDATIONS))
        animes.append (anime)
        getID = True
        # Loop var
        count+=1

print("\n......................................................");
print("               ***SUGGESTIONS***");
print("......................................................");

for anime in animes:
    print (anime.title.encode('utf-8'))

#endregion Main
