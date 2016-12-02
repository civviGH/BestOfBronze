import random
import json
from HelperFunctions import *
from time import sleep
from flask import Flask, flash, redirect, render_template

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
      print("Found a ranked game")
      # get game data
      print("Fetching info")
      sleep(0.5)
      content = giveGameData(summonerId)
      # read summoner ids of every player
      print("Fetching summoner ids")
      sleep(0.5)
      summonerIds = getSummonerIdsFromContent(content)
      # get name of every summoner 
      print("Converting Summoner ids to Names")
      sleep(0.5)
      summonerNames = getSummonerNames(summonerIds)
      # read champion ids 
      print("Fetching champion ids")
      sleep(0.5)
      championIds = getChampionIdsFromContent(content)
      # get champion names
      print("Converting Champion ids to Names")
      sleep(0.5)
      championNames = []
      for id in championIds:
        championNames.append(getChampionName(id))
      # make list of summonerids with champ ids
      summoners = []
      for i in range(10):
        summoners.append([summonerNames[i], championNames[i]])
      # if someone is ingame, print template for match view
      print("Rendering template")
      return render_template("ingame.html", summoners = summoners)
  # if no one is ingame, go back to index
  flash('Did not find any1 ingame.')
  return redirect('/')

webapi.run()  
