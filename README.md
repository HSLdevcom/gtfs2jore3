# gtfs2jore3

Changes Matkahuolto GTFS data (or any other GTFS data) to GIRO Hastus 2016 export file format, which Jore3 -- and possibly Jore4 due to Hastus integration needs -- reads. Filters only trips that are U routes and only for stops that are saved in Jore for that route.

## Requirements
- Python 3
- So far tested only on Linux (Debian 11)

## How to use
1. Fetch GTFS from operator. Most are available on [NAP](https://finap.fi). For example U453-U465 are [here](https://finap.fi/#/service/60/60).
2. Save GTFS to the same folder as these scripts.
3. Check config.txt and adjust as needed. You can add special days by adding those on "tarkastelupäivät". Use Jore3's special day codes, such as JU for Juhannuspäivä. For some routes it is required to add override values for stop codes that are conflicting or missing for HSL area in Matkahuolto's data. This is currently done for Kamppi, Porvoo and Metsäkyläntie.
4. Fetch all routes from Jore3, use Hastus 2016 format. Save it as a 7%.txt to this folder.
5. Run gtfs2jore3.py
6. Upload the generated files from folder results-to-be-uploaded to Jore.

## Documentation
- [GTFS](https://developers.google.com/transit/gtfs)
- Hastus-Jore is documented in internal documentation "Hastus aikataulujen siirto Joreen ja Kolaan, rajapinnan kuvaus" (this uses version 12.5.2021)

## TODO
- Special days doesn't have "lisä" notes
- Trips that start between 00:00-04:30 are uploaded for the next day, not according to usual convention to previous day for hours 24:00->28:30
- All stops that are Hastus places are marked as a Hastus places for a route errorneously.
- Allow configuring different data source for HSL's routes.