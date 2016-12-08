import random
import json
from HelperFunctions import *
from time import sleep
from flask import Flask, flash, redirect, render_template, request

webapi = Flask(__name__)

# start by reading database once
# reads the whole database into summonerList: id,tier
summonerList = []
with open("SummonerList.txt", "r") as SL:
  for line in SL:
    # line[:-1] cuts out the \n appendix
    summonerList.append(line[:-1])

# shuffe the list to randomize search order
random.shuffle(summonerList)

@webapi.route('/')
@webapi.route('/<name>')
def index(name=None):
  return render_template("index.html", name = name)

# webinterface to add players to the database by name
@webapi.route('/action/addSummonerByName')
def addSummonerByName(name=None):
  # the message that will be shown in the template, wether adding was successful or not
  message = ""
  # the league the player is in
  league = ""
  return render_template("addSummoner.html", name=name, message = message, league = league)  

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
  random.shuffle(summonerList)
  return redirect('/')

# looks for game, prints template if it finds one
@webapi.route('/db/find-game')
def findGame():
  for summoner in summonerList:
    summonerId = int(summoner[:summoner.find(",")])
    # sleeps are added to ensure the maximum number of api calls does not exceed limits
    sleep(1.5)
    if checkIfIngame(summonerId):
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

      # make list of summonernames with champnames
      summoners = []
      for i in range(10):
        summoners.append([gameInformation[i][2], gameInformation[i][3]])

      # if someone is ingame, print template for match view
      print("Rendering template")
      return render_template("ingame.html", summoners = summoners)

  # if no one is ingame, go back to index
  flash('Did not find any1 ingame.')
  return redirect('/')

webapi.run()  
