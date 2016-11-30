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
def index():
  return "hi"
  
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
  for summoner in summonerList:
    tmp = tmp + summoner + "<br>"
  return tmp
  
@webapi.route('/db/shuffle-library')
def shuffleLibrary():
  global summonerList
  random.shuffle(summonerList)
  return redirect('/')

@webapi.route('/find-game')
def findGame():
  for summoner in summonerList:
    summonerId = summoner[:summoner.find(",")]
    #print("checking if summoner {} is ingame...").format(summonerId)
    sleep(1)
    if checkIfIngame(int(summoner[:summoner.find(",")])):
      #print(summoner + " is ingame")
      return (summoner[:summoner.find(",")] + " is ingame. \o/")
  return "no one is ingame :-/"

webapi.run()  