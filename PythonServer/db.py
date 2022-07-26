import mysql.connector
from mysql.connector import Error
import math
connection = None

# Function called for adding a specific location in the DB
def insertLocation(timestamp, latitude, longitude, Class):
  query = "INSERT INTO VibrationData(longitude, latitude, class, timestamp) VALUES ('"+ str(longitude) +"', '" + str(latitude) + "', '" + Class +"', '"+ timestamp+"')"
  execute_query(query)

# Function called for reading locations in a radius of a certain amount of kilometers from a given location
def readLocations(longitude, latitude, km):
  query = "SELECT longitude, latitude, class, timestamp FROM VibrationData WHERE SQRT(POW(69.1 * (latitude - "+ str(latitude) + " ), 2) + POW(69.1 * ("+ str(longitude) + " - longitude) * COS(latitude / 57.3), 2)) < " + str(km)
  result = []
  query_result = read_query(query)
  for row in query_result:
    result.append({
    "timestamp": row[3],
    "longitude": row[0],
    "latitude": row[1],
    "class": row[2]
    })
  return result

# Threshold function
# need half of the records in a non-coherent class to switch the state of a macro-zone,
# if more than 100 samples are present in the DB, we select a higher denominator
# switching from l/2 to l/(log10l), to avoid to wait for too many samples
def threshold(len):
    if(len <= 100):
        return int(len/2)
    else:
        return int(len/math.log(len, 10))

# Function reading the amount of samples in the macro-zone and returning the proper threshold
def readThreshold(latitude, longitude):
    list = readLocations(longitude, latitude, 0.005)
    return threshold(len(list))

# Function for updating the macro-zone
# update score = min(score+1, threshold) if class == ACCESSIBLE
# update score = max(score-1, threshold) if class == INACCESSIBLE
# i.e. create a window between -threshold and +threshold
def updateMacroZone(id, score, longitude, latitude, Class):
  threshold = readThreshold(latitude, longitude)
  if Class == "INACCESSIBLE":
      if score-1 < -threshold:
          score = -threshold
      else:
          score = score-1
      print("Updating Macro-Zone INACCEESSIBLE(-1) ID=",id,"Score=",score,"Threshold=", threshold)
      query = "UPDATE VibrationCumulativeData SET score = " + str(score) + ", bound = " + str(threshold) + " WHERE id = " + str(id)
  else:
      if score+1 > threshold:
          score = threshold
      else:
          score = score+1
      print("Updating Macro-Zone ACCESSIBLE(+1) ID=",id,"Score=",score,"Threshold=", threshold)
      query = "UPDATE VibrationCumulativeData SET score = " + str(score) + ", bound = " + str(threshold) + " WHERE id = " + str(id)
  execute_query(query)

# Function for inserting a new macro-zone
def insertMacroZone(longitude, latitude, Class):
  if Class == "INACCESSIBLE":
      query = "INSERT INTO VibrationCumulativeData(LATITUDE, LONGITUDE, SCORE,BOUND) VALUES("+ str(latitude) + "," + str(longitude) + "," + str(1) + ",1)"
  else:
      query = "INSERT INTO VibrationCumulativeData(LATITUDE, LONGITUDE, SCORE,BOUND) VALUES(" + str(latitude) + "," + str(longitude) + "," + str(-1) + ",1)"
  execute_query(query)

# Function to read the closest macro-zone's informations
def readClosestMacroZone(longitude, latitude, km):
  query = "SELECT id, score FROM VibrationCumulativeData WHERE SQRT(POW(69.1 * (latitude - "+ str(latitude) + " ), 2) + POW(69.1 * ("+ str(longitude) + " - longitude) * COS(latitude / 57.3), 2)) < " + str(km) + "LIMIT 1"
  result = []
  query_result = read_query(query)
  for row in query_result:
      result.append({
          "id": row[0],
          "score": row[1]
      })
  return result

# Function to read all locations' information
def readAllLocations():
  query = "SELECT longitude, latitude, class, timestamp FROM VibrationData"
  result = []
  query_result = read_query(query)
  for row in query_result:
      result.append({
          "timestamp": row[3],
          "longitude": row[0],
          "latitude": row[1],
          "class": row[2]
      })
  return result

# Function to read all Macro-zones' information
def readAllMacroZones():
  query = "SELECT longitude, latitude, score, bound FROM VibrationCumulativeData WHERE score <= 0"
  result = []
  query_result = read_query(query)
  for row in query_result:
      result.append({
          "longitude": row[0],
          "latitude": row[1],
          "score": row[2],
          "bound": row[3]
      })
  return result

# Function used to create/update macro-zones
def insertCumulativeInaccessibleLocation(latitude, longitude, Class):
    result = readClosestMacroZone(longitude, latitude, 0.005)
    if result != []:
        updateMacroZone(result[0]['id'], result[0]['score'], longitude, latitude, Class)
    else:
        print("Inserting New Macro-Zone")
        insertMacroZone(longitude, latitude, Class)

def execute_query(query):
    global connection
    if connection == None:
        connectDB()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

def read_query(query):
  global connection
  if connection == None:
      connectDB()
  cursor = connection.cursor()
  cursor.execute(query)
  result = cursor.fetchall()
  return result

def connectDB():
    db_name = "Wheelchairs"
    user = "user"
    password = "password"
    host="127.0.0.1"
    global connection
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=db_name, port=3306)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()