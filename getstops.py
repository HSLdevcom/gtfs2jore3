#!/usr/bin/python3
import requests

# Gets all stops from Digitransit API: Creates a dictionary where key is the short code and value is the long code.

def query(configuration):
 question = """
 {
  stops {
   code
   gtfsId
   }
 }
 """
 request = requests.post('https://api.digitransit.fi/routing/v2/hsl/gtfs/v1?digitransit-subscription-key=' + configuration['digitransitapikey'], json={'query': question})
 if request.status_code== 200:
  pys = request.json()
  result = {}
  for x in pys.values():
   for y in x.values():
    for z in y:
     tunnus = z['gtfsId']
     tunnus = tunnus[-7:]
     result[z['code']] = tunnus
  return(result)
 else:
  raise Exception("ei vastausta graphql-serverilta")

if __name__ == "__main__":
 print(query())
