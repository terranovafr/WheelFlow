### Project
This is the project containing the python server, responsible for handling the interaction with the database, perform the data preprocessing and classification task and expose a RestFUL API to be used by the Android Application.

### Python files
main.py: contains the functions to be called in case of a request to a  RestFUL API

db.py: contains the functions to interact with the DB

dataProcessing.py: contains the functions to process the data

model.pkl: contains the classification model to be used to classify the instances

### Disclaimer 
The server IP address and port should be provided to the Android Application. We've used ngrok.io to generate a temporary IP address for the server.