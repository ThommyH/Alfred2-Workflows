import PyAl
import urllib2
import json
import datetime
import time
import sys
from workflow import Workflow, web

DATE = ""
BURGERMODE = False

def parseInputParam():
  input = "{query}"
  offset = 0
  if input == "": 
    offset = 0
  elif input == "morgen":
    offset = 1
  elif input == "burger":
    offset = (4 - datetime.date.today().weekday())%6
    globals()["BURGERMODE"] = True
  globals()["DATE"] = (datetime.date.today() + datetime.timedelta(days=offset)).strftime("%Y-%m-%d")

def crawlData(url):
  try:
    r = web.get(url)
    # Parse the JSON returned by pinboard and extract the posts
    result = r.json()
    return result
  except:
    return []

def checkNotAvail(data, wf, image):
  if not data:
    return True
  return False

def parseTitleSubtitle(item):
  text_title = item["name"]
  text_split = text_title.split(" ")
  title = ""
  subtitle = item['category'] + " "
  for word in text_split:
    if len(title+word) < 90:
      title += word + " "
    else:
      subtitle += word + " "
  return title, subtitle

def getDataOpenMensa(mensaId = 0):
  url = "http://openmensa.org/api/v2/canteens/"+str(mensaId)+"/days/" + DATE + "/meals"
  return crawlData(url)

def setMensaGriebnitzsee(wf):
  data = getDataOpenMensa(62)
  if checkNotAvail(data, wf, "mensa-logo.png"): return
  for item in getDataOpenMensa(62):
    title, subtitle = parseTitleSubtitle(item)
    wf.add_item(title=title, subtitle=subtitle, arg="http://google.de", valid=True, icon="mensa-logo.png")

def setTastys(wf):
  data = getDataOpenMensa(104)
  if checkNotAvail(data, wf, "tastys.png"): return
  for item in data:
    if (not globals()["BURGERMODE"] or "BURGER" in item['name']):
      title, subtitle = parseTitleSubtitle(item)
      wf.add_item(title=title, subtitle=subtitle, icon="tastys.png")

def setUlf(wf):
  data = getDataOpenMensa(112)
  if checkNotAvail(data, wf, "ulf.png"): return
  for item in data:
    title, subtitle = parseTitleSubtitle(item)
    wf.add_item(title=title, subtitle=subtitle, icon="ulf.png")
  
def main(wf):
  if not globals()["BURGERMODE"]:
    setMensaGriebnitzsee(wf)
    setUlf(wf)
  setTastys(wf)
  wf.send_feedback()

if __name__ == "__main__":
  parseInputParam()
  wf = Workflow()
  sys.exit(wf.run(main))
  
