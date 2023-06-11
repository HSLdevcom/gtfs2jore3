#!/usr/bin/python3
import os
import csv
from datetime import datetime
from datetime import timedelta
import json

def alltripsgtfstohastus(configuration, date, datetype):
 kaavio = configuration['kaavio']
 liikennoitsija = configuration['liikennoitsija']
 ulinelist = listulines()
 with open('tmp/trips-output.txt', 'r') as gtfstrips:
  gtfstrips = csv.reader(gtfstrips,delimiter=",")
  with open('tmp/trips-' + str(date) + '.txt', 'w',encoding="latin-1") as joretrips:
   joretrips = csv.writer(joretrips,delimiter=";")
   output = []
   for a in gtfstrips:
    if str(a[2]) == str(date):
#Row 4 requires Jore3 Hastus place codes, getstoptimesparameters determines those and returns a list of first and last hastus place as well as distance, duration etc which are also available
     stoptimesparameters = getstoptimesparameters(a[1])
     fromhastus = stoptimesparameters[0]
     tohastus = stoptimesparameters[1]
     tripdistance = stoptimesparameters[2]
#calculate trip duration, needs some modification to cope with more than 24 hour clock
     tripendtime = joretime(str(stoptimesparameters[4]))
     tripstarttime = joretime(str(stoptimesparameters[3]))
     tripduration = tripendtime - tripstarttime
     tripendtime = str(tripendtime)[11:][:5]
     tripstarttime = str(tripstarttime)[11:][:5]
     tripduration = int(tripduration.total_seconds() / 60)
#Trip route and variant is in routes.txt gtfs file
     tripdetails = getrouteparameters(a[1], ulinelist)
     triproute = tripdetails[0]
     if triproute != None:
      tripvariant = tripdetails[1]
      tripdirection = int(a[6])
      isfriday = None
      if datetype == 'pe':
       isfriday = a[7]
      output.append(['4', a[1][:6], str(kaavio) + str(a[1])[:6] ,None, fromhastus, tohastus, triproute,3,None,1])
      output.append(['5', liikennoitsija, a[1][:6], str(kaavio) + str(a[1])[:6], a[1][:6], '0', triproute, None, tripvariant, tripstarttime, tripendtime, tripduration, 3, 1, tripdistance, 0, isfriday, None, tripdirection, 1, 0, 0, 0])
      for c in writestoprecord(a[1], tripdistance):
       output.append(c)
   for b in output:
       joretrips.writerow(b)

def joretime(time):
    hours, rest = time.split(':', 1)
    time = timedelta(hours=int(hours)) + datetime.strptime(rest, "%M")
    return time

def gethastuspaikkaforstop(stopcode):
    with open('tmp/stops-output.txt', 'r') as stoplist:
        stoplist = csv.reader(stoplist,delimiter=',')
        for b in stoplist:
            if b[0] == stopcode:
                return b[5]

def writestoprecord(tripid, distance):
 with open('tmp/stop_times-output.txt', 'r') as stoptimeslist:
  stoptimeslist = csv.reader(stoptimeslist,delimiter=',')
  result = []
  stopcounter = 0
  for a in stoptimeslist:
   if a[0] == tripid:
    stopcounter += 1
    if stopcounter == 1:
     stopdistance = round(float(0), 1)
    else:
     stopdistance = round(((float(a[8]) * 1000 ) - stoplocation), 1)
    stoplocation = float(a[8]) * 1000
    makejustintegerfromtime = dict.fromkeys(map(ord, ':'), None)
    stoptime = a[3].translate(makejustintegerfromtime)[:-2]
    hastuspaikka = gethastuspaikkaforstop(a[1])
    if hastuspaikka != '':
     if str(a[8]) == str(distance) or str(a[8]) == str(0.0):
      tstpstopcode = 'T'
     else:
       tstpstopcode = 'R'
    else:
     tstpstopcode = None
    result.append(['6', tripid[:6], hastuspaikka, a[1], None, None, None, None, stoptime, stopdistance, tstpstopcode, None])
  return result

def getrouteparameters(tripid, ulines):
#Returns route and variant according to trip id
 with open('tmp/trips.txt', 'r') as tripslist:
  tripslist = csv.reader(tripslist, delimiter=",")
  for b in tripslist:
   if b[1] == tripid:
    tripid = b[0]
 with open('tmp/routes.txt', 'r') as routeslist:
  routeslist = csv.reader(routeslist, delimiter=",")
  for a in routeslist:
   if a[1] == tripid:
    result = []
#Blacklists F as well as numbers due to Onnibus Flex tendency to add F in front of line code. This also means that bus line with a variant letter F, such as 455F, won't work. At the moment no such variant exists
    removenumbers = str(a[2]).maketrans('0123456789F', '           ')
    removeletters = str(a[2]).maketrans('ABCDFGHIJKLNMOPQRSTUVXVZÅÄÖ', '                           ')
    route = str(a[2]).translate(removeletters)
    route = route.replace(' ', '')
    route = str(7) + route
    variant = str(a[2]).translate(removenumbers)
    variant = variant.replace(' ', '')
    code = route + variant
    for a in ulines:
     if str(a) == str(code):
      result.append(route)
      result.append(variant)
      return result
 return [None, None]

def listulines():
 with open('7%.txt', 'r', encoding='latin-1') as ulines:
  ulines = csv.reader(ulines,delimiter=';')
  ulinelist = []
  for c in ulines:
   if c[0] == "rvariant":
    uline = str(c[5])
    uline = uline[:-1]
    ulinelist.append(uline)
  return ulinelist

def getstoptimesparameters(tripid):
 with open('tmp/stops-output.txt', 'r') as stopslist:
  stopslist = csv.reader(stopslist,delimiter=",")
  with open('tmp/stop_times-output.txt', 'r') as stoptimeslist:
   stoptimeslist = csv.reader(stoptimeslist,delimiter=",")
   minstopsequence = float('inf')
   maxstopsequence = 0
   tripdistance = 0
   firststopdistance = 0
   arrivaltime = 0
   departuretime = 0
   firststopcode = 0
   laststopcode = 0
   for a in stoptimeslist:
    counter = 0
    if a[0] == tripid:
     if int(a[5]) < minstopsequence:
      minstopsequence = int(a[5])
      departuretime = a[3][:5]
      firststopcode = a[1]
      firststopdistance = float(a[8])
     if int(a[5]) > maxstopsequence:
      maxstopsequence = int(a[5])
      tripdistance = float(a[8])
      arrivaltime = a[2][:5]
      laststopcode = a[1]
  tripdistance = tripdistance - firststopdistance
  tripdistance = round(tripdistance, 1)
#Now we have hsl stop codes for first and last stop stored in result
#We must match those to Hastus codes
  result = [firststopcode, laststopcode, tripdistance, departuretime, arrivaltime]
  for c in stopslist:
   if result[0] == c[0]:
     result[0] = c[5]
   if result[1] == c[0]:
     result[1] = c[5]
 return(result)

if __name__ == "__main__":
 import sys
 try:
  with open('config.txt', 'r') as configurationfile:
   configuration = json.load(configurationfile)
   alltripsgtfstohastus(configuration,sys.argv[1])
 except:
  print('Please provide date as a command line argument in format DDMMYYYY, make sure tmp folder contains preprocessed trips.txt (named trips-output.txt) and make sure that config.txt is present in this folder')
