from HelperFunctions import *
import random
from time import sleep
from flask import Flask, redirect, render_template

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
    summonerId = summoner[:summoner.find(",")]
    sleep(1)
    if checkIfIngame(int(summoner[:summoner.find(",")])):
      # if someone is ingame, print template for match view
      return render_template("ingame.html", )
  # if no one is ingame, go back to index
  return redirect('/')

webapi.run()  