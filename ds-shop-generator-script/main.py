from json import load, dump
from os.path import isfile
from requests import get
from bs4 import BeautifulSoup

TMPData = {}

unistore = {
  "storeInfo": {
    "title": "DS Shop",
    "author": "TheOzymandias",
    "description": "A collection of DS games, sourced from Internet Archive. Thanks to andrigamerita, Kodi &amp; SPMC Canada, Cylum, Combono, and the-game-collection",
    "file": "ds-shop.unistore",
    "url": "https://github.com/The0zymandias/ds-shop/raw/main/ds-shop.unistore",
    "sheet": "",
    "sheetURL": "",
    "bg_index": 0,
    "bg_sheet": 0,
    "version": 3,
    "revision": 1
  },
  "storeContent": []
}

def endsWith(string, sub):
  ml, sl, = len(string), len(sub)
  return string[ml-sl:] == sub

def main():
  #get user input, determine which parts run
  global TMPData, unistore
  buildTMPFile = input("Build TMP File? [y/n]: ").lower() == "y"
  buildUNIFile = input("Build unistore File? [y/n]: ").lower() == "y"
  if buildUNIFile:
    buildUNIFromTMP = input("Build unistore from premade TMP? [y/n]: ").lower() == "y"
    if buildUNIFromTMP:
      baseTMPFilePath = ""
      while not(isfile(baseTMPFilePath)):
        baseTMPFilePath = input("Give TMP File: ")
  else:
    buildUNIFromTMP = False

  #this if-else chain loads the data needed for the unistore
  if buildUNIFromTMP:
    try:
      with open(baseTMPFilePath, "r") as file:
        TMPData = load(file)
        
    except FileNotFoundError:
      return "params file does not exist."
      
  elif buildTMPFile or buildUNIFile:
    try:
      #gets the list of urls to get links from
      with open("params.json", "r") as file:
        installLocatDat = load(file)
        
    except FileNotFoundError:
      return "params file does not exist."
      
    for url in installLocatDat["storeList"]: 
      #removes possible issues with combining sub-links later
      url = url.removesuffix("/")
      print(f"Reading {url}...") 
      url = url+"/"

      #gets the html from the url
      tempReqs = get(url)
      HTMLSoup = BeautifulSoup(tempReqs.text, 'html.parser')
      
      for link in HTMLSoup.find_all('a'):
        currentLink = str(link.get('href'))
        currentLinkText = link.get_text()

        #makes sure the file is of the correct type and preps the filename for display in the unistore
        if endsWith(currentLink, ".7z"):
          currentLinkText = currentLinkText.removesuffix(".7z")
          
        elif endsWith(currentLink, ".zip"): 
          currentLinkText = currentLinkText.removesuffix(".zip")
          
        elif endsWith(currentLink, ".nds"):
          currentLinkText = currentLinkText.removesuffix(".nds")
          
        else:
          continue

        #this section gets the name of the unistore item and gets the "variation" of it (usually region)
        w = currentLinkText.find("(")
        if w == -1:
          currentTitle = currentLinkText
          
        else:
          currentTitle = currentLinkText[0:w]
          sections = []
          x = 0
          
          while True:
            y = currentLinkText.find("(", x)
            
            if y != -1:
              z = currentLinkText.find(")", y)
              
              if z != -1:
                sections.append(currentLinkText[y:z+1])
                x = z
                
              else:
                break
                
            else:
              break
              
          if currentLinkText.find("[b]") != -1:
            sections.append("[b]")
        
        currentTitle, currentOption = currentTitle.rstrip(), "".join(sections) or currentTitle.rstrip()
        print(f"Trying to add {currentTitle} {currentOption}")

        #adds the data to TEMPData
        #why add to TEMPData and not the unistore? well, unistore files list items via index in a list, 
        #not by the names assiciated with the item. By adding them to TEMPData under the same name, i can
        #cluster all roms under the same name together in the unistore
        
        try:
          bool(TMPData[currentTitle])
          
        except KeyError:
          TMPData[currentTitle] = {}
        TMPData[currentTitle][currentOption] = url+currentLink
        print("Success")

  
  #builds the requested files
  if buildTMPFile:
    print("Building tmp file...")
    with open("ds-shop.tmp", "w") as file:
      dump(TMPData, file)
  if buildUNIFile:
    print("Building unistore file...")
    for k, v in TMPData.items():
      tempItem = {
        "info": {
          "title": k,
          "author": "",
          "version": "",
          "category": ["game"],
          "console": ["NDS","3DS"],
          "description": "",
          "license": "",
          "icon_index": 0,
          "sheet_index": 0,
          "last_updated": ""
          }
        }
      for k2, v2 in v.items():
        if endsWith(v2, ".7z"): 
          typeVal = ".7z"
          
        elif endsWith(v2, ".zip"): 
          typeVal = ".zip"
          
        elif endsWith(v2, ".nds"): 
          typeVal = ".nds"
          
        else: 
          continue

        if typeVal == ".7z" or typeVal == ".zip":
          tempItem[k2] = [
            {
            "type": "downloadFile",
            "file": v2,
            "output": f"sdmc:/temp{typeVal}"
                },
                {
            "type": "extractFile",
            "file": f"sdmc:/temp{typeVal}",
            "input": "",
            "output": f"%NDS%/{k} {k2}.nds"
                },
                {
            "type": "deleteFile",
            "file": f"sdmc:/temp{typeVal}"
            }
          ]
        elif typeVal == ".nds":
          tempItem[k2] = [
            {
          "type": "downloadFile",
          "file": v2,
          "output": f"%NDS%/{k} {k2}.nds"
            }
          ]
        
      if len(tempItem) > 1:
        unistore["storeContent"].append(tempItem)
        
    with open("ds-shop.unistore", "w") as file:
      dump(unistore, file)


if __name__ == "__main__":
  print(main())
