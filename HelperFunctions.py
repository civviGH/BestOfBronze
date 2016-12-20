import requests
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from pprint import pprint

def addSummonerToList(summonerId):
  with open("SummonerList.txt", "a") as SummonerList:
    SummonerList.write(str(summonerId) + "\n")

def clearSummonerList():
  open("SummonerList.txt", "w").close()

def checkIfSummonerExists(summonerId):
  with open("SummonerList.txt", "r") as SummonerList:
    for line in SummonerList:
      if line[:-1] == str(summonerId):
        return True
    return False  

def removeSummoner(summonerId):
  SummonerList = open("SummonerList.txt", "r+")
  content = SummonerList.readlines()
  SummonerList.seek(0)
  for line in content:
    if line[:-1] != str(summonerId):
      SummonerList.write(line)
  SummonerList.truncate()
  SummonerList.close()

def checkForHighElo():
  summonerList = []
  summonersToDelete = []
  blocksOfTen = 0
  with open("SummonerList.txt", "r") as content:
    for summoner in content:
      summonerList.append(summoner)
  blocksOfTen = len(summonerList)/10

  for i in range(blocksOfTen):
    listToCheck = []
    for j in range(i*10, (i+1)*10):
      listToCheck.append(summonerList[j][:-1])
    summonersToDelete = summonersToDelete + checkIfStillBronze(listToCheck)
  listToCheck = []
  for i in range(blocksOfTen*10, len(summonerList)):
    listToCheck.append(summonerList[i][:-1])
  summonersToDelete = summonersToDelete + checkIfStillBronze(listToCheck)
  for summoner in summonersToDelete:
    removeSummoner(summoner)
  return len(summonersToDelete)

def checkIfStillBronze(listToCheck):
  listOfIds = ""
  deleteSummoners = []
  with open('config.json') as data_file:
    config = json.load(data_file)
  for summoner in listToCheck:
    listOfIds = listOfIds + str(summoner) + ","
  response = requests.get("https://euw.api.pvp.net/api/lol/euw/v2.5/league/by-summoner/" + listOfIds[:-1] + "/entry?api_key=" + config["api-key"])
  if response.status_code != 200:
    print("Bad Riot API request.")
    return None
  content = json.loads(response.text)
  for key,value in content.iteritems():
    for league in value:
      if league["queue"] == "RANKED_SOLO_5x5":
        if league["tier"] != "BRONZE":
          deleteSummoners.append(key)
        elif (league["entries"][0]["division"] != "V") and (league["entries"][0]["division"] != "IV"):
          deleteSummoners.append(key)
  return deleteSummoners

def checkIfIngame(summonerId, timePlayed):
  with open('config.json') as data_file:
    config = json.load(data_file)
    rankedQueues = config["ranked-queues"]
    response = requests.get("https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/" + str(summonerId) + "?api_key=" + config["api-key"]) 
  if (response.status_code == 503):
    print("Cant check if ingame, return code is 503")
  if response.status_code == 200:
    content = json.loads(response.text)
    if content["gameType"] == "CUSTOM_GAME":
      return False
    if content["gameQueueConfigId"] in rankedQueues:
      if (timePlayed == 0) or (content["gameLength"] + 3 <= timePlayed*60.0):
        return True
      else:
        print("Found a ranked game, but time played is too high. <{}>".format(str((content["gameLength"]/60) + 3)))      
  return False

def giveGameData(summonerId):
  with open("config.json") as data_file:
    config = json.load(data_file)
    response = requests.get("https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/EUW1/" + str(summonerId) + "?api_key=" + config["api-key"]) 
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

def getChampionNameById(championId):
  try:
    with open ("static/champion.json") as data_file:
     champions = json.load(data_file)
  except:
    print("Static data not found. Please update static data.")
    return ""
  for key,value in champions["data"].iteritems():
    if int(value["key"]) == championId:
      return value["id"]
  print("Encountered champion id i dont know, trying to request it")
  with open("config.json") as data_file:
    config = json.load(data_file)
  response = requests.get("https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/" + str(championId) + "?api_key=" + config["api-key"])
  content = json.loads(response.text)
  champName = content["name"]
  print("I guess its " + champName + " (" + str(championId) + ")")
  print("Please update your static data to prevent additional requests to be necessary.")
  return champName

def getSummonerIdByName(summonerName):
  with open("config.json") as data_file:
    config = json.load(data_file)
    response = requests.get("https://euw.api.pvp.net/api/lol/euw/v1.4/summoner/by-name/" + summonerName + "?api_key=" + config["api-key"])
  if response.status_code != 200:
    print("Could not retrieve summoner name because of bad api request.")
    return 0
  content = json.loads(response.text)
  return content[summonerName.lower()]["id"]

def getSummonerNamesById(summonerIds):
  listOfIds = ""
  for id in summonerIds:
    listOfIds = listOfIds + str(id) + ","
  with open("config.json") as data_file:
    config = json.load(data_file)
    response = requests.get("https://euw.api.pvp.net/api/lol/euw/v1.4/summoner/" + listOfIds[:-1] + "?api_key=" + config["api-key"])
  if response.status_code != 200:
    print("Could not retrieve summoner names because of bad api request")
    return ""
  content = json.loads(response.text)
  summonerNames = []
  for key,summoner in content.iteritems():
    summonerNames.append(summoner["name"])
  return summonerNames

def getSummonerNames(gameInformation):
  listOfIds = ""
  for summoner in gameInformation:
    listOfIds = listOfIds + str(summoner["summonerId"]) + ","
  with open("config.json") as data_file:
    config = json.load(data_file)
    response = requests.get("https://euw.api.pvp.net/api/lol/euw/v1.4/summoner/" + listOfIds[:-1] + "?api_key=" + config["api-key"])
  if response.status_code != 200:
    print("Could not retrieve summoner names because of bad api request")
    return ""
  content = json.loads(response.text)
  for summoner in gameInformation:
    for key,value in content.iteritems():
      if value["id"] == summoner["summonerId"]:
        summoner["summonerName"] = value["name"]
  return gameInformation

def getChampionNames(gameInformation):
  for summoner in gameInformation:
    summoner["championName"] = getChampionNameById(summoner["championId"])
  return gameInformation

def getGameInformation(content):
  gameInformation = []
  for participant in content["participants"]:
    tempDic = {}
    tempDic["summonerId"] = int(participant["summonerId"])
    tempDic["championId"] = int(participant["championId"])
    tempDic["spellIds"] = [participant["spell1Id"],participant["spell2Id"]]
    gameInformation.append(tempDic)
  return gameInformation

def forgeDataDragonLinks(gameInformation):
  with open("config.json") as data_file:
    config = json.load(data_file)
  for summoner in gameInformation:
    ddlink = "http://ddragon.leagueoflegends.com/cdn/" + config["data-dragon-version"] + "/img/champion/" + summoner["championName"] + ".png"
    summoner["ddlink"] = ddlink
  return gameInformation

def forgeSummonerSpellLinks(gameInformation):
  with open("config.json") as data_file:
    config = json.load(data_file)
  with open("static/summoner.json") as data_file:
    staticSpellData = json.load(data_file)
  for summoner in gameInformation:
    summonerLinks = []
    for spellId in summoner["spellIds"]:
      for key,value in staticSpellData["data"].iteritems():
        if value["key"] == str(spellId):
          spellName = value["image"]["full"]
          summonerLinks.append("http://ddragon.leagueoflegends.com/cdn/" + config["data-dragon-version"] + "/img/spell/" + spellName)
    summoner["spellLinks"] = summonerLinks
  return gameInformation

def getDataDragonVersion():
  response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
  content = json.loads(response.text)
  return str(content[0])
  
def getChampionStatics(ddv):
  response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + ddv + "/data/en_US/champion.json")
  if response.status_code == 200:
    content = response.text.encode('utf-8')
    with open("static/champion.json", "w") as champs:
      champs.write(content)
    return None
  return "Did not fetch champion static data. Return code was " + str(response.status_code + ".")
  
def getSummonerSpellStatics(ddv):
  response = requests.get("http://ddragon.leagueoflegends.com/cdn/" + ddv + "/data/en_US/summoner.json")
  if response.status_code == 200:
    content = response.text.encode('utf-8')
    with open("static/summoner.json", "w") as summoner:
      summoner.write(content)
    return None
  return "Did not fetch summoner spells static data. Return code was " + str(response.status_code + ".")
  
def getLeagueEntryById(summonerId):
  with open("config.json") as data_file:
    config = json.load(data_file)
  response = requests.get("https://euw.api.pvp.net/api/lol/euw/v2.5/league/by-summoner/" + str(summonerId) + "?api_key=" + config["api-key"])
  if response.status_code != 200:
    return None
  content = json.loads(response.text)
  for league in content[str(summonerId)]:
    if league["queue"] == "RANKED_SOLO_5x5":
      return league["entries"]
  return None
  
def getBronzePlayers(league):
  playerList = []
  for entry in league:
    if entry["division"] == "V":
      playerList.append(entry["playerOrTeamId"])
  return playerList

def forgeSpectatorString(content):
  spectatorString = ""
  
  with open("config.json") as data_file:
    config = json.load(data_file)

  spectatorString = spectatorString + "\"" + config["app-folder"] + "League of Legends\\RADS\\solutions\\lol_game_client_sln\\releases\\" + config["app-version"] + "\\deploy\\League of Legends.exe\""

  spectatorString = spectatorString + " 8394 LoLLauncher.exe \"\" \"spectator spectator.euw1.lol.riotgames.com:80"

  spectatorString = spectatorString + " " + content["observers"]["encryptionKey"]

  spectatorString = spectatorString + " " + str(content["gameId"])

  spectatorString = spectatorString + " EUW1\""
  return spectatorString
  
