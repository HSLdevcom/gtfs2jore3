#!/usr/bin/python3
import csv
import json
import datetime
import os
import writetrip
import preprocess
import requests

#writes the output file

def writecsv(datetype, pvm, humanreadableday, nextdate):
 date = datetime.date.today()
 date = date.strftime('%Y%m%d')
 time = datetime.datetime.now(tz=None)
 time = time.strftime('%H%M%S')
 with open('results-to-be-uploaded/' + configuration['kaavio'] + '-' + pvm + '-result.exp', 'w', newline='', encoding='latin-1') as csvfile:
   jorewriter = csv.writer(csvfile, delimiter=';')
   jorewriter.writerow([1,'HASTUS','HSL','1.04',date,time])
   jorewriter.writerow([2,configuration['booking'],configuration['kausi'],configuration['kaavio'],datetype,configuration['alkupvm'],configuration['loppupvm'],configuration['liikennoitsija']])
   jorewriter.writerow([3,configuration['kaavio'],datetype,'00','HSL',datetype,configuration['alkupvm'],configuration['loppupvm'],time])
#Rows 4-6, which include separate trips
   stoptimesandtripsforjore = writetrip.alltripsgtfstohastus(configuration, humanreadableday, nextdate, pvm)
   for trips in stoptimesandtripsforjore:
    jorewriter.writerow(trips)

if __name__ == "__main__":
#get configuration and preprocess gtfs data
 with open('config.txt', 'r') as configurationfile:
  configuration = json.load(configurationfile)
 preprocess.preprocess_everything(configuration)

#get Hastus parameters
 with open('hastusparameters.txt', 'r') as hastusparameters:
  hastuspar = json.load(hastusparameters)
 dates = configuration['tarkastelupaivat']
#loops through dates from which the output file should be generated
 for i in dates:
  humanreadableday = configuration['tarkastelupaivat'][i]
# provides the next date in order to handle Jore's 30h clock
  nextdate = datetime.datetime.strptime(humanreadableday, "%Y%m%d")
  nextdate += datetime.timedelta(days=1)
  nextdate = str(nextdate)[:10]
  nextdate = nextdate.replace('-', '')
  try:
   datetype = hastuspar[i]
  except:
   datetype = i
  writecsv(datetype, i, humanreadableday, nextdate)
