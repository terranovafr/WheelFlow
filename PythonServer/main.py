import traceback
from flask import Flask, request, jsonify
import json
import geopy.distance
from db import readLocations, readAllLocations, insertLocation, readAllMacroZones, insertCumulativeInaccessibleLocation
from dataProcessing import *
import warnings

app = Flask(__name__)

# GET /locations/inaccessible - endpoint for retrieving all inaccessible locations' scores
# If parameters are present, find all inaccessible locations in a radius of x km from the source,
# where x is the geodesic distance in kilometers from source to destination
# i.e. all possible inaccessible locations along the route (to be checked at the front-end once
# received the route from the Google Maps API)
@app.route('/locations/inaccessible', methods=['GET'])
def getInaccessibleLocations():
    try:
        if(request.args.get("source_longitude") and request.args.get("source_latitude") and
            request.args.get("dest_longitude") and request.args.get("dest_latitude")):
            print("/locations/inaccessible?x - New request asking for inaccessible locations in a specific path...")
            source_longitude = request.args.get("source_longitude")
            source_latitude = request.args.get("source_latitude")
            dest_longitude = request.args.get("dest_longitude")
            dest_latitude = request.args.get("dest_latitude")
            coords_1 = (source_longitude, source_latitude)
            coords_2 = (dest_longitude, dest_latitude)
            km = geopy.distance.geodesic(coords_1, coords_2).km
            results = readLocations(source_longitude, source_latitude, km)
            return json.dumps(results, default=str)
        else:
            print("/locations/inaccessible - New request asking for all inaccessible locations...")
            results = readAllLocations()
            return json.dumps(results, default=str)
    except:
        return jsonify({'trace': traceback.format_exc()})


# GET /locations/inaccessible/scores - endpoint for retrieving all inaccessible macro-zones' scores
@app.route('/locations/inaccessible/scores', methods=['GET'])
def getInaccessibleCumulativeLocations():
    try:
        print("/locations/inaccessible/scores - New request asking for all inaccessible locations' scores...")
        results = readAllMacroZones()
        return json.dumps(results, default=str)
    except:
        return jsonify({'trace': traceback.format_exc()})

# POST /locations/update - endpoint for receiving updates from contributors
# Preprocess the data, classify the data and update the DB
@app.route('/locations/update', methods=['POST'])
def postLocationsUpdates():
    if request.method == 'POST':
        print("/locations/update - New request sending an update...")
        if type(request.json["data"]) is str:
            data = json.loads(request.json["data"])
        else:
            data = request.json["data"]
        df = pd.DataFrame()
        for element in data:
            timestamp = element['timestamp']
            latitude = element['latitude']
            longitude = element['longitude']
            if latitude == "0.000000" and longitude == "0.000000":
                continue
            acc_x = element['ACC_X']
            acc_y = element['ACC_Y']
            acc_z = element['ACC_Z']
            gyr_x = element['GYR_X']
            gyr_y = element['GYR_Y']
            gyr_z = element['GYR_Z']
            mag_x = element['MAG_X']
            mag_y = element['MAG_Y']
            mag_z = element['MAG_Z']
            new_row = pd.DataFrame({'timestamp': timestamp, 'latitude': latitude, 'longitude': longitude, 'ACC_X': acc_x, 'ACC_Y': acc_y, 'ACC_Z': acc_z, 'GYR_X': gyr_x, 'GYR_Y': gyr_y, 'GYR_Z': gyr_z, 'MAG_X': mag_x, 'MAG_Y': mag_y, 'MAG_Z': mag_z}, index=[0])
            df = pd.concat([new_row, df.loc[:]], ignore_index=True)
            df = df.sort_values(by=['timestamp'])
        #return "Successful update!"
        print("Received dataframe:")
        print(df)
        df_new = preprocess(df)
        print("Result of preprocessing phase:")
        print(df_new)
        df_classified = classify(df_new)
        print("Adding entries to the DB...")
        for row_index in df_classified.index:
            # Inserting information about the specific (latitude, longitude)
            insertLocation(df_classified.iloc[row_index, 0],df_classified.iloc[row_index, 1], df_classified.iloc[row_index, 2], df_classified.iloc[row_index, -1])
            # Inserting information about the macro-zone
            insertCumulativeInaccessibleLocation(df_classified.iloc[row_index, 1], df_classified.iloc[row_index, 2], df_classified.iloc[row_index, -1])
        return "Successful update!"

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    app.run(debug=True, port="5002")
