#!/usr/bin/python3
import os
import sys
import fileinput
import getstops
from datetime import datetime
import tripfilter
import json
import csv
from zipfile import ZipFile

def init_folders_and_data(configuration):
 if os.path.isdir('tmp') == False:
  os.mkdir('tmp')
 if os.path.isdir('results-to-be-uploaded') == False:
  os.mkdir('results-to-be-uploaded')
 try:
  with ZipFile(configuration['gtfspaketti']) as zip:
   zip.extractall(path='tmp')
 except:
  raise Exception('GTFS file is missing from this folder. Please download ' + configuration['gtfspaketti'] + ' to this folder. For further information, see Readme')

def get_hastusplaces_for_stop():
 with open('7%.txt', 'r', encoding='latin-1') as routesjore:
  routesjore = csv.reader(routesjore, delimiter=';')
#Get hastusplaces from Jore data
  hastusplaces = {}
  for a in routesjore:
   if a[0] == 'stop':
    hastusplaces[str(a[1])] = str(a[7])
 return hastusplaces

def modify_stops(configuration, stopcodelist, hastusplaces):
 os.chdir('tmp')
 # First, modify stop dictionary to HSL codes and stops.txt
 # initialize dictionary, which in the end will have a matkahuolto stop code as a key and hsl key as a value
 matkahuoltotohsl = {}
 counter = 0
 with open('stops.txt', newline='') as stopsgtfs:
  stopsgtfs = csv.reader(stopsgtfs, delimiter=',')
  with open('stops-output.txt', 'w', newline='') as stopsoutput:
   stopsoutput = csv.writer(stopsoutput, delimiter=',')
   for row in stopsgtfs:
# Prints a header
    if counter == 0:
     stopsoutput.writerow(row)
     counter =+ 1
    else:
     for mhstopor, hslstopor in configuration['yliajettavatpysakit'].items():
      if row[0] == mhstopor:
       hsl = hslstopor
       mh = mhstopor
       row[0] = hsl
       matkahuoltotohsl.update({mh: hsl})
      else:
       try:
        hsl = stopcodelist[row[4]]
       except:
        hsl = None
       mh = row[0]
       if hsl != None:
        row[0] = hsl
        matkahuoltotohsl.update({mh: hsl})
# Add hastus places
     row[5] = hastusplaces.get(row[0])
     stopsoutput.writerow(row)
     counter =+ 1
 os.chdir('..')
 return(matkahuoltotohsl)

def modify_stoptimes(matkahuoltotohsl):
 os.chdir("tmp")
 counter = 0
 with open('stop_times.txt', newline='') as stoptimesgtfs:
  stoptimesgtfs = csv.reader(stoptimesgtfs, delimiter=',')
  with open('stop_times-output.txt', 'w', newline='') as stoptimesoutput:
   stoptimesoutput = csv.writer(stoptimesoutput, delimiter=',')
   for row in stoptimesgtfs:
    if counter == 0:
     stoptimesoutput.writerow(row)
    else:
     try:
         row[1] = matkahuoltotohsl[row[1]]
         stoptimesoutput.writerow(row)
     except:
      pass
    counter =+ 1
 os.chdir("..")

def listulines():
 with open('7%.txt', 'r', encoding='latin-1') as ulines:
  ulines = csv.reader(ulines,delimiter=';')
  ulinelist = []
  for c in ulines:
   if c[0] == "rvariant":
    uline = str(c[5])
    uline = uline[:-1]
    ulinelist.append(uline)
  with open('tmp/ulinelist.txt', 'w') as output:
   for a in ulinelist:
    output.write(a + '\n')

def fridaynighttrips():
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
  mato = configuration["tarkastelupaivat"]["mato"]
  pe = configuration["tarkastelupaivat"]["pe"]
  la = configuration["tarkastelupaivat"]["la"]
  with open('tmp/trips-output-phase1.txt', 'r', newline='') as tripsoutput:
   gtfstrips = csv.reader(tripsoutput,delimiter=",")
#  with open('tmp/trips-' + str(date) + '.txt', 'w',encoding="latin-1") as joretrips:
#   joretrips = csv.writer(joretrips,delimiter=";")
   frisatnighttrips = []
   for a in gtfstrips:
    if str(a[2]) == str(la) and datetime.strptime(a[5], "%H%M") < datetime.strptime("0430", "%H%M"):
     frisatnighttrips.append(a[1])

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
   for a in frisatnighttrips:
    fridayonlyservice.append(a)
#   print(fridayonlyservice)
 with open('tmp/trips-output.txt', 'w', newline='') as trips:
  with open('tmp/trips-output-phase1.txt', 'r', newline='') as phase1:
   phase1 = csv.reader(phase1,delimiter=",")
   for b in phase1:
    for q in fridayonlyservice:
     towrite = b
     if b[1] == q:
      towrite[7] = 'p'
      pass
    output = csv.writer(trips,delimiter=",")
    output.writerow(towrite)

# with open('tmp/fridayservice.txt', "w") as output:
#  for a in fridayonlyservice:
#   output.write(a)
#   output.write('\n')

def preprocess_everything(configuration):
 init_folders_and_data(configuration)
 matkahuoltotohsl = modify_stops(configuration, getstops.query(configuration), get_hastusplaces_for_stop())
 modify_stoptimes(matkahuoltotohsl)
 listulines()
 tripfilter.filtertrips()
 fridaynighttrips()

if __name__ == "__main__":
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
 preprocess_everything(configuration)
