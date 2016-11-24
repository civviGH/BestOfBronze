from HelperFunctions import *
import random
from time import sleep

# reads the whole database into summonerList: id,tier
summonerList = []
with open("SummonerList.txt", "r") as SL:
  for line in SL:
    # line[:-1] cuts out the \n appendix
    summonerList.append(line[:-1])

# shuffe the list to randomize search order
random.shuffle(summonerList)

for summoner in summonerList:
  summonerId = summoner[:summoner.find(",")]
  print("checking if summoner {} is ingame...").format(summonerId)
  sleep(1)
  if checkIfIngame(int(summoner[:summoner.find(",")])):
    print(summoner + " is ingame")
