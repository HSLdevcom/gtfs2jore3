#!/usr/bin/python3
import csv
import json
import os
import writetrip

def listmatkahuoltocalendardates():
# Returns a dictionary where key is trip's Matkahuolto id and values are list of dates, listed in configuration, when it is run
 matkahuoltodates = {}
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
 dates = configuration["tarkastelupäivät"]
 with open('tmp/calendar_dates.txt', 'r') as calendar:
  calendar = csv.reader(calendar,delimiter=',')
  for a in calendar:
   for b, c in dates.items():
    if c == a[1]:
     try:
      len(matkahuoltodates[a[0]])
      matkahuoltodates[a[0]].append(c)
     except KeyError:
      matkahuoltodates[a[0]] = []
      matkahuoltodates[a[0]].append(c)
 return matkahuoltodates

def getdirection2destinations():
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
  return configuration["suunta2määränpäät"]

def getfridayonlyservice(serviceid):
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
  mato = configuration["tarkastelupäivät"]["mato"]
  pe = configuration["tarkastelupäivät"]["pe"]
  with open('tmp/calendar_dates.txt', 'r') as caldates:
      caldates = csv.reader(caldates, delimiter=',')
      weekservice = []
      fridayservice = []
      for g in caldates:
          if g[1] == pe:
              fridayservice.append(g[0])
          if g[1] == mato:
              weekservice.append(g[0])
 fridayonlyservice = list(set(fridayservice) - set(weekservice))
 for z in fridayonlyservice:
     if z == serviceid:
        return 'p'
     else:
        return None

#Fill trips-output with U-lines only and fix directions as well as imput notes for fridays
def filtertrips():
 with open('tmp/trips.txt', newline='') as tripsgtfs:
  tripsgtfs = csv.reader(tripsgtfs, delimiter=',')
  with open('tmp/trips-output.txt', 'w', newline='') as tripsoutput:
   tripsoutput = csv.writer(tripsoutput, delimiter=',')
   counter = 0
   for row in tripsgtfs:
    if counter == 0:
     tripsoutput.writerow(row)
     counter =+ 1
    else:
# Check if route is a valid U route
     if writetrip.getrouteparameters(row[0], writetrip.listulines())[0] != None:
#     print(validroutes)
      validdates = listmatkahuoltocalendardates()
      direction2destinations = getdirection2destinations()
      friday = getfridayonlyservice(row[2])
      if friday == 'p':
       row[7] = 'p'
      for b in validdates.items():
       if b[0] == row[2]:
        for k in b[1]:
         row[2] = k
#Direction
         for c in direction2destinations:
          if row[3] != c:
              row[6] = 1
          else:
              row[6] = 2
              break
#Modify routecodes to HSL version
         if len(row[4]) == 3:
             row[4] = str(7) + str(row[4])
         if len(row[4]) == 2:
             row[4] = str(70) + str(row[4])
         if len(row[4]) == 1:
             row[4] = str(700) + str(row[4])
         tripsoutput.writerow(row)

if __name__ == "__main__":
 try:
  print(filtertrips())
 except:
  print('Requires a GTFS trips.txt file in tmp folder in order to be run separately')
