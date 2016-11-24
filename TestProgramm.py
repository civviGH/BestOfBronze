from HelperFunctions import *

clearSummonerList()

for i in range(10):
  addSummonerToList(i, "B5")

if checkIfSummonerExists(5):
  print("5 gibt es")
else:
  print("irgendwie nich gefunden")

removeSummoner(5)

if checkIfSummonerExists(5):
  print("5 gibt es")
else:
  print("irgendwie nich gefunden")

addSummonerToList(100, "B3")
addSummonerToList(101, "S5")

for i in range(10):
  if not checkIfSummonerExists:
    addSummonerToList0(i, "B5")

checkForHighElo()
