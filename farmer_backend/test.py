import requests
import json

link = "http://my.metoblue.com/dataset/query?apikey=bjb2jbeig193uvv"

my_data = {
    "units": {
        "temperature": "C",
        "velocity": "km/h",
        "length": "metric",
        "energy": "watts"
    },
    "geometry": {
        "type": "MultiPoint",
        "coordinates": [[7.57327, 47.558399, 279]], 
        "locationNames": ["Basel"]
    },
    "format": "json",
    "timeIntervals": ["2019-01-01T+00:00/2019-12-31T+00:00"],
    "timeIntervalsAlignment": "none",
    "queries": [
        {
            "domain": "NEMSGLOBAL",
            "gapFillDomain": None,
            "timeResolution": "hourly",
            "codes": [
                {
                    "code": 157,
                    "level": "180-0 mb above gnd"
                }
            ]
        }
    ]

}

response = requests.post(link, json=my_data)
print(response)  