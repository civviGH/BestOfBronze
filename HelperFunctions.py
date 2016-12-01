import requests
import config
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def addSummonerToList(summonerId, tier):
  with open("SummonerList.txt", "a") as SummonerList:
    SummonerList.write(str(summonerId) + "," + tier + "\r\n")

def clearSummonerList():
  open("SummonerList.txt", "w").close()

def checkIfSummonerExists(summonerId):
  with open("SummonerList.txt", "r") as SummonerList:
    for line in SummonerList:
      if line[:line.find(",")] == str(summonerId):
        return True
    return False  

def removeSummoner(summonerId):
  SummonerList = open("SummonerList.txt", "r+")
  content = SummonerList.readlines()
  SummonerList.seek(0)
  for line in content:
    if line[:line.find(",")] != str(summonerId):
      SummonerList.write(line)
  SummonerList.truncate()
  SummonerList.close()

def checkForHighElo():
  SummonerList = open("SummonerList.txt", "r+")
  content = SummonerList.readlines()
  SummonerList.seek(0)
  for line in content:
    if line[line.find(",")+1:] == "B5\n" or  line[line.find(",")+1:] == "B4\n":
      SummonerList.write(line)
  SummonerList.truncate()
  SummonerList.close()

def checkIfIngame(summonerId):
  response = requests.get("https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/" + str(summonerId) + "?api_key=" + config.static["api-key"]) 
  print(response.status_code)
  if (response.status_code == 503):
    print("Cant check if ingame, return code is 503")
  if response.status_code == 200:
    content = json.loads(response.text)
    if content["gameQueueConfigId"] in config.static["ranked-queues"]:
      return True
  return False

def giveGameData(summonerId):
  response = requests.get("https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/36728651?api_key=" + config.static["api-key"]) 
  if (response.status_code == 503):
    print("Cant give game data, return code is 503")
  if response.status_code == 200:
    return json.loads(response.text)
  return False