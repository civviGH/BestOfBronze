import random
import json
import sys
import pyperclip
from HelperFunctions import *
from time import sleep
from flask import Flask, flash, redirect, render_template, request
from Tkinter import Tk

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
  print("Did not find a database. Creating an empty one. Please add summoners by using populate function.")
  print("Start again to use empty database.")
  print("Dont forget ")
  foo = open("SummonerList.txt", "w+")
  sys.exit()
  
# check if config exists. if not, create an empty one
try:
  with open("config.json", "r") as data_file:
    pass
except:
  print("Did not find config file. Creating empty one.")
  print("Please fill in the App-Folder, App-Version and API-Key.")
  config = {}
  config["data-dragon-version"] = ""
  config["app-folder"] = ""
  config["api-key"] = ""
  config["ranked-queues"] = [440, 420]
  config["app-version"] = ""
  with open("config.json", "w") as data_file:
    json.dump(config, data_file)
  sys.exit()
# shuffe the list to randomize search order
random.shuffle(summonerList)

# list for already searched summoners
alreadySearched = []

@webapi.route('/db/populate')
def populateDatabase():
  added = 0
  summonerName = request.args.get("summonerName")
  summonerName = summonerName.replace(" ","")
  summonerId = getSummonerIdByName(summonerName)
  print(summonerId)
  if summonerId == 0:
    flash("Failed to request Id from Riot API.")
    return redirect('/')
  league = getLeagueEntryById(summonerId)
  listOfSummoners = getBronzePlayers(league)
  for id in listOfSummoners:
    if not checkIfSummonerExists(id):
      added += 1
      addSummonerToList(id)
  flash("Added {} new players to the database.".format(str(added)))
  return redirect('/')

@webapi.route('/')
def index(name=None):
  return render_template("index.html", name = name)

@webapi.route('/db/read-database')
def readDatabase():
  global summonerList
  global alreadySearched

  # reads the whole database into summonerList: id,tier
  summonerList = []
  with open("SummonerList.txt", "r") as SL:
    for line in SL:
      # line[:-1] cuts out the \n appendix
      summonerList.append(line[:-1])

  # shuffe the list to randomize search order
  random.shuffle(summonerList)
  flash ("Re-read Database entries.")
  if len(alreadySearched) > 0:
    alreadySearched = []
    flash("Resetted the already-searched list.")
  return redirect('/')

@webapi.route('/db/print-database')
def printDatabase():
  global summonerList
  flash('{} players found in database'.format(len(summonerList)))
  return redirect('/')
  
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
        flash("You should not look for games with negative playing time.")
        return redirect('/')
    except:
      flash("Time played has to be an integer.")
      return redirect('/')
  else:
    timePlayed = 0
  for summoner in summonerList:
    summonerId = int(summoner)
    print("Looking for <{}>".format(str(summonerId)))
    if (summonerId in alreadySearched):
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
      if gameInformation == "":
        flash("Failed to retrieve Summoner Names. Bad API request.")
        return redirect('/')
      # should now be [{summonerId championId spellIds summonerName} ... ]

      # get champion names
      sleep(0.5)
      gameInformation = getChampionNames(gameInformation)
      # should now be [{summonerId championId spellIds championName summonerName} ... ]
      
      # forge data dragon links for champion icons
      gameInformation = forgeDataDragonLinks(gameInformation)
      # should now be [{summonerId championId spellIds championName summonerName ddlink} ... ]

      # forge data dragon links for summoner spells
      gameInformation = forgeSummonerSpellLinks(gameInformation)
      # should now be [{summonerId championId spellIds championName summonerName ddlink spellLinks} ... ]
    
      # forge spectator code, copy it to clipboard
      spectatorString = forgeSpectatorString(content)
      pyperclip.copy(spectatorString)

      # make list of summonernames with champnames
      summoners = []
      for i in range(10):
        summoners.append([gameInformation[i]["summonerName"], gameInformation[i]["ddlink"], gameInformation[i]["spellLinks"]])
      
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
  if not ddv:
    flash('Riot certificate not valid.')
    return redirect('/')
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

@webapi.route('/test')
def test():
  hits = checkForHighElo()
  flash('Removed {} high elo player(s) from database.'.format(hits))
  return redirect('/')

webapi.run(debug=True, port=5000)  
