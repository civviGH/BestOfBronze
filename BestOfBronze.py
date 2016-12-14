import random
import json
import sys
from HelperFunctions import *
from time import sleep
from flask import Flask, flash, redirect, render_template, request

from pprint import pprint

webapi = Flask(__name__)
webapi.secret_key = 'bestofbronze_secret'

# start by reading database once
# reads the whole database into summonerList: id,tier
summonerList = []
try:
  with open("SummonerList.txt", "r") as SL:
    for line in SL:
      # line[:-1] cuts out the \n appendix
      summonerList.append(line[:-1])
except:
  print("Did not find a database. Creating an empty one. Please add one summoner by hand and then migrate.")
  print("Start again to use empty database.")
  foo = open("SummonerList.txt", "w+")
  sys.exit()
# shuffe the list to randomize search order
random.shuffle(summonerList)

# list for already searched summoners
alreadySearched = []

@webapi.route('/test')
def test():
  with open('config.json') as data_file:    
    data = json.load(data_file)
    pprint(data)
  return ""

@webapi.route('/')
def index(name=None):
  global alreadySearched
  if len(alreadySearched) > 0:
    alreadySearched = []
    flash("Resetted the already-searched list.")
  return render_template("index.html", name = name)

# webinterface to add players to the database by name
@webapi.route('/action/addSummonerByName')
def addSummonerByName(name=None, tier=None):
  name = request.args.get("name")
  tier = request.args.get("tier")
  # get summoner id from name
  summonerId = getSummonerIdByName(name)
  if (summonerId == 0) or (tier is None):
    flash("Failed to request Id or tier is not specified.")
  else:
    if checkIfSummonerExists(summonerId):
      flash("{} already found in database.".format(name))
      return redirect('/')
    flash("Added {} in tier {} to database.".format(name, tier))
    addSummonerToList(summonerId, tier)
  return redirect('/')

@webapi.route('/db/read-database')
def readDatabase():
  global summonerList
  # reads the whole database into summonerList: id,tier
  summonerList = []
  with open("SummonerList.txt", "r") as SL:
    for line in SL:
      # line[:-1] cuts out the \n appendix
      summonerList.append(line[:-1])

  # shuffe the list to randomize search order
  random.shuffle(summonerList)
  flash ("Re-read Database entries.")
  return redirect('/')

@webapi.route('/db/print-database')
def printDatabase():
  global summonerList
  tmp = ""
  # concatenate database and print as huge string
  for summoner in summonerList:
    tmp = tmp + summoner + "<br>"
  return tmp
  
# shuffle library for whatever reason
@webapi.route('/db/shuffle-library')
def shuffleLibrary():
  global summonerList
  flash ("Shuffled library.")
  random.shuffle(summonerList)
  return redirect('/')

# looks for game, prints template if it finds one
@webapi.route('/db/find-game')
def findGame():
  global summonerList
  global alreadySearched
  timePlayed = request.args.get("timePlayed")
  if timePlayed:
    try:
      timePlayed = int(timePlayed)
      if timePlayed < 0:
        flash("U should not look for game with negative playing time.")
        return redirect('/')
    except:
      flash("Time played has to be an integer.")
      return redirect('/')
  else:
    timePlayed = 0
  for summoner in summonerList:
    summonerId = int(summoner[:summoner.find(",")])
    print("Looking for <{}>".format(str(summonerId)))
    if (summonerId in alreadySearched):
      print("Already looked for it.")
      print("---")
      continue
    else:
      alreadySearched.append(summonerId)
      
    # sleeps are added to ensure the maximum number of api calls does not exceed limits
    sleep(1.5)
    if checkIfIngame(summonerId, timePlayed):
      print("Found a ranked game of id <{}>".format(summonerId))

      # get game data
      print("Fetching game content.")
      sleep(0.5)
      content = giveGameData(summonerId)

      # read summoner ids of every player
      print("Fetching summoner ids.")
      sleep(0.5)
      # maybe later used for database growth
      summonerIds = getSummonerIdsFromContent(content)

      # fetch game information [id, champ, summoner spells..] for every player
      print("Fetching game information.")
      sleep(0.5)
      gameInformation = getGameInformation(content)
      # gameInformation now is [{summonerId championId spellIds} ... ]

      # get name of every summoner 
      print("Looking up names of the players.")
      sleep(0.5)
      gameInformation = getSummonerNames(gameInformation)
      # should now be [{summonerId championId spellIds summonerName} ... ]

      # get champion names
      sleep(0.5)
      gameInformation = getChampionNames(gameInformation)
      # should now be [{summonerId championId spellIds championName summonerName} ... ]
      
      # forge data dragon links for champion icons
      gameInformation = forgeDataDragonLinks(gameInformation)
      # should now be [{summonerId championId spellIds championName summonerName ddlink} ... ]

      # make list of summonernames with champnames
      summoners = []
      for i in range(10):
        summoners.append([gameInformation[i]["summonerName"], gameInformation[i]["ddlink"]])
      
      # calculate timePlayed
      ingameTime = (content["gameLength"]/60) + 3
      
      # if someone is ingame, print template for match view
      print("Rendering template")
      return render_template("ingame.html", summoners = summoners, ingameTime = ingameTime)

  # if no one is ingame, go back to index
  flash('Did not find anyone ingame with given search parameters.')
  flash('Resetted the already-searched list.')
  alreadySearched = []
  return redirect('/')

  
@webapi.route('/static/update')
def updateStatics():
  # get data dragon version once, pass it into other getters
  ddv = getDataDragonVersion()
  fails = 0
  answer = getChampionStatics(ddv)
  if answer:
    flash(answer)
    fails += 1
    
  answer = getSummonerSpellStatics(ddv)
  if answer:
    flash(answer)
    fails += 1
    
  # flash a success message if there are no errors
  if fails == 0:
    flash("All static data has been updated successfully. Running on version " + ddv + ".")
  
  with open("config.json") as data_file:
    config = json.load(data_file)
    config["data-dragon-version"] = ddv
  
  with open("config.json", "w") as data_file:
    json.dump(config, data_file)
    
  return redirect('/')

webapi.run()  
