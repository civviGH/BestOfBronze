from ChampionDictionary import championDic
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
  response = requests.get("https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/" + str(summonerId) + "?api_key=" + config.static["api-key"]) 
  if (response.status_code == 503):
    print("Cant give game data, return code is 503")
    return ""
  if response.status_code == 200:
    return json.loads(response.text)
  print("giveGameData() does unwanted stuff")
  return ""

def getSummonerIdsFromContent(content):
  summonerIds = []
  for participant in content["participants"]:
    summonerIds.append(int(participant["summonerId"]))
  return summonerIds

def getChampionIdsFromContent(content):
  championIds = []
  for participant in content["participants"]:
    championIds.append(int(participant["championId"]))
  return championIds 

def getChampionName(championId):
  try:
    return championDic[championId]
  except:              
    print("Encountered champion id i dont konw, trying to request it")
    response = requests.get("https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/" + str(championId) + "?api_key=" + config.static["api-key"])
    content = json.loads(response.text)
    champName = content["name"]
    print("I guess its " + champName + " (" + str(championId) + ")")
    print("Please add the missing champion to the ChampionDictionary.py and commit")
    return champName

def getSummonerNames(summonerIds):
  listOfIds = ""
  for id in summonerIds:
    listOfIds = listOfIds + str(id) + ","
  response = requests.get("https://euw.api.pvp.net/api/lol/euw/v1.4/summoner/" + listOfIds[:-1] + "?api_key=" + config.static["api-key"])
  if response.status_code != 200:
    print("Could not retrieve summoner names because of bad api request")
    return ""
  content = json.loads(response.text)
  print(type(content))
  summonerNames = []
  for key,summoner in content.iteritems():
    summonerNames.append(summoner["name"])
  return summonerNames