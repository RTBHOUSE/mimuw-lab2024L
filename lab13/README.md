# Cloud computing

We will create a service which periodically gathers meteo forecast data for Warsaw, stores it in a database and exposes 
the latest available forecast in the form of a database view. We will use Google Cloud Platform services such as: BigQuery, 
Cloud Functions, Pub/Sub and Cloud Scheduler.

## 1. Create Google Cloud project
Create a new google cloud project or use an existing one if you have already (*[Instructions](https://cloud.google.com/apigee/docs/hybrid/v1.5/precog-gcpproject/)*). 

Note: you will need to setup a billing account with a credit card if you haven't already done so.

## 2. Create messaging topic
Create a new Pub/Sub topic named "weather_update_trigger_topic" (on the left-hand side of the *[Panel](https://console.cloud.google.com)* you will
find "Pub/Sub" under the "Analytics" section)

## 3. Create scheduler job
Create a new job in Cloud Scheduler called "weather_download_trigger_job" that will every minute send message 
(with any body, it is not relevant) on the Pub/Sub topic created in the previous point.

## 4. Create BigQuery table
Create in BigQuery a new dataset "weather" and in this dataset a new table "weather_forecast" with the following columns:

| name | type | NULLABLE? |
| --- | --- | --- |
| datetime | DATETIME | NULLABLE |
| weather | STRING | NULLABLE |
| temp | INTEGER | NULLABLE |
| timestamp | TIMESTAMP | NULLABLE |

## 5. Create function
Create a new function in Cloud Function that will be triggered by the Pub/Sub topic "weather_update_trigger_topic". 
Runtime should be set to Python 3.9, entry point: "main" and the following two source code files:

main.py
```
import json
import requests as re
from datetime import datetime, timedelta
from google.cloud import bigquery

def main(event, context): 
   # Construct a BigQuery client object. client = bigquery.Client(YOUR_GCP_PROJECT_NAME)
   # Get latest weather forecast for Warsaw
   answer = re.get("https://www.7timer.info/bin/civil.php?lon=21&lat=52.2&ac=0&unit=metric&output=json") 
   answer_json = json.loads(answer.text) 
   init_date = datetime.strptime(answer_json['init'], '%Y%m%d%H') 
   rows_to_insert = [] 
   for forecast in answer_json['dataseries']: 
      curr_date = init_date + timedelta(hours=forecast['timepoint']) 
      curr_temp = forecast['temp2m'] 
      curr_weather = forecast['weather'] 
      rows_to_insert.append({"datetime": curr_date.strftime('%Y-%m-%d %H:%M:%S'), "weather": curr_weather, "temp": curr_temp, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}) 
      
   # Stream latest weather forecast data to BigQuery 
   errors = client.insert_rows_json('weather.weather_forecast', rows_to_insert) 
   if errors == []: 
      print("New rows have been added.") 
   else: 
      print("Encountered errors while inserting rows: {}".format(errors))
```

requirements.txt
```
# Function dependencies, for example:
# package>=version
google-auth>=1.11.3
google-cloud-bigquery>=1.24.0
requests>=2.27.1
```

## 6. Test 
Test the function
Note: There is a dedicated option "Test" next to the function in Cloud Functions

## 7. Validate
Check if new entries arrive every minute to BigQuery table "weather_forecast".

## 8. Expose
Create a new view in BigQuery in "weather" dataset, named "latest_weather_forecast"
defined as follows:
```
SELECT 
   * EXCEPT (row_number, timestamp)
FROM ( 
   SELECT 
      *, ROW_NUMBER() OVER (PARTITION BY timestamp ORDER BY timestamp DESC) AS row_number 
   FROM ( 
      SELECT 
         * 
      FROM 
         `weather.weather_forecast` 
   ) )
WHERE row_number = 1
```

This view is deduplicating data from weather_forecast table, presenting onlythose with the latest "timestamp" value.

## 9. Get the latest weather forecast for Warsaw
Query the "latest_weather_forecast" view to get the latest weather forecastfor Warsaw for the given date and hour:
```
SELECT * from weather.latest_weather_forecast WHERE DATE(datetime)="2022-06-09"
```

## 10. Weather forecast for many locations 
Imagine you would like to gather the weather forecast for many locations
* How would you change the schema of the table?
* How can we limit the money charged when querying temperatures for a given location?
