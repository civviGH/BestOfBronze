import random
import json
import config
from HelperFunctions import *
from time import sleep
from flask import Flask, flash, redirect, render_template, request

webapi = Flask(__name__)
webapi.secret_key = 'bestofbronze_secret'

# start by reading database once
# reads the whole database into summonerList: id,tier
summonerList = []
with open("SummonerList.txt", "r") as SL:
  for line in SL:
    # line[:-1] cuts out the \n appendix
    summonerList.append(line[:-1])

# shuffe the list to randomize search order
random.shuffle(summonerList)

@webapi.route('/test')
def test():
  return ""

@webapi.route('/')
@webapi.route('/<name>')
def index(name=None):
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
  timePlayed = request.args.get("timePlayed")
  if timePlayed:
    try:
      timePlayed = int(timePlayed)
    except:
      flash("Time played has to be an integer.")
      return redirect('/')
  else:
    timePlayed = 0
  for summoner in summonerList:
    summonerId = int(summoner[:summoner.find(",")])
    # sleeps are added to ensure the maximum number of api calls does not exceed limits
    sleep(1.5)
    if checkIfIngame(summonerId, timePlayed):
      print("Found a ranked game of id <{}>".format(summonerId))

      # get game data
      print("Fetching info")
      sleep(0.5)
      content = giveGameData(summonerId)

      # read summoner ids of every player
      print("Fetching summoner ids")
      sleep(0.5)
      # maybe later used for database growth
      summonerIds = getSummonerIdsFromContent(content)

      # fetch game information [id, champ..] for every player
      print("Fetching game information")
      sleep(0.5)
      gameInformation = getGameInformation(content)
      # should be [ [id,champid] , ... ]

      # get name of every summoner 
      print("Converting Summoner ids to Names")
      sleep(0.5)
      gameInformation = getSummonerNames(gameInformation)
      # should now be [ [id,champid,sName] , ... ]

      # get champion names
      sleep(0.5)
      gameInformation = getChampionNames(gameInformation)
      # should now be [ [id,champid,sName,cName] , ... ]
      
      # forge data dragon links for champion icons
      gameInformation = forgeDataDragonLinks(gameInformation)
      # should now be [ [id,champid,sName,cName,ddlink] , ... ]

      # make list of summonernames with champnames
      summoners = []
      for i in range(10):
        summoners.append([gameInformation[i][2], gameInformation[i][4]])
      
      # calculate timePlayed
      ingameTime = (content["gameLength"]/60) + 3
      
      # if someone is ingame, print template for match view
      print("Rendering template")
      return render_template("ingame.html", summoners = summoners, ingameTime = ingameTime)

  # if no one is ingame, go back to index
  flash('Did not find anyone ingame with given search parameters.')
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
  return redirect('/')

webapi.run()  
