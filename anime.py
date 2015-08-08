import argparse
from bs4 import BeautifulSoup
import cookielib
import httplib
import logging
import os.path
from random import randint
import sys
import urllib
import urllib2

COOKIEFILE = 'cookies.lwp'
MIN_ID=1
MAX_ID=11000

class Anime(object):
  id = -1
  title = ""

  def __init__ (self, id, title):
    self.id = id
    self.title = title

def lookupMAL(title, userId, password):
  url = "http://%s:%s@myanimelist.net/" % (userId, password)

# Returns the title represented by the anime id as per Anime News Network (ANN).
# Returns 'None' if the entry corresponding to this id does not exist, or
# represents a Manga entry.
def getTitle(animeId):
  animeId = 1408
  url = "http://myanimelist.net/anime.php?id=%s" %  str(animeId)
  username = "arya5691"
  password = "kind>reqd<3"

  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  login_data = urllib.urlencode({'username' : username, 'j_password' : password})
  resp = opener.open(url, login_data)
  print resp.read()
  resp = opener.open(url)
  print resp.read()
  for index, cookie in enumerate(cj):
    print index, '  :  ', cookie
  try:
    print "a"
# print response.info()
#parsedHtml = BeautifulSoup(html, "lxml")
#   print parsedHtml# .find("div", {"id": "contentWrapper"}) # .find("h1", {"id": "page_header"}).contents[0]
#   for index, cookie in enumerate(cj):
#    print index, '  :  ', cookie
#   cj.save(COOKIEFILE)
  except urllib2.HTTPError, e:
    logging.warning('HTTPError = %s, animeId = %s' % (str(e.code), str(animeId)))
  except urllib2.URLError, e:
    logging.warning('URLError = %s, animeId = %s' % (str(e.reason), str(animeId)))
  except httplib.HTTPException, e:
    logging.warning('HTTPException, animeId = %s' % str(e))
  except Exception:
    import traceback
    logging.warning('generic exception: ' + traceback.format_exc())
 
# Returns a random Integer between |MIN_ID| and |MAX_ID|, both inclusive.
def getRandomId():
  return randint(MIN_ID, MAX_ID)

if __name__ == "__main__":

  visited = set()

  while (True):
    animeId = getRandomId()
    if (animeId in visited):
      continue
    visited.add(animeId)
    animeTitle = getTitle(animeId)
    print animeTitle
    break
      
  parser = argparse.ArgumentParser()
  # username + password.
  # Allow movies?
  parser.add_argument('--threshold', required=True, type=int, help="Minimum allowed rating as per MyAnimeList")
  args = parser.parse_args()
  print args

  print getTitle(100)
