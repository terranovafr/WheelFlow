# WheelFlow 
WheelFlow is an **Android Application** that focuses on collecting and sharing geo-localized **accessibility information** about routes in order to assist **wheelchair users**. 
Users can search for a path from a source to a destination and receive accessibility information about the path.
<br>
The core of the application is the collection of vibration data based on crowdsourcing: route contributor users can collect data using their smartphone while they are on the move and share it with a web server responsible for classifying the data and handling the routing requests.<br>
**Machine Learning** techniques will enable the smart application to classify routes as accessible or not.
<p align="center"><img width="720" alt="Screenshot 2023-07-05 alle 20 39 28" src="https://github.com/terranovaa/WheelFlow/assets/61695945/94717edc-13b6-4f4b-9564-3fc1ecf4ae6f"></p>

 ## Project Architecture
 The architecture is composed of a Python server and two Android Client applications.
 <ul>
  <li>The Python server stores the model used to classify the data, handles the interaction with the database, and answers the clients’ requests allowing users to ask for routing information taking into consideration the accessibility of the locations.</li>
  <li>A main Android application allows the user to get an overview of the accessibility barriers, contribute by collecting data in the city, and search for a route from a source to a destination.</li>
  <li>Another Android client application is fully dedicated to data collection.</li>
 </ul>
<p align="center"><img width="463" alt="Screenshot 2023-07-05 alle 20 39 54" src="https://github.com/terranovaa/WheelFlow/assets/61695945/820daf3a-c2a4-45b5-a9b0-39036b37b138"></p>

## Project Structure
The project is organized as follows:
- PythonServer/ contains the source code of a centralized Python server handling the crowdsourcing from many Android apps in a client-server fashion.
- DataCollection/ contains the Android source code of the application dedicated to the data collection.
- DataAnalysis/ contains the Python scripts used for analyzing the data and using different machine learning techniques.
- AndroidApplication/ contains the Android source code of the main Android application providing all the required features.
  
Each folder will contain a readMe file explaining more in detail each of the modules.
<br>A SQL file is also present for re-creating the structure of the database.
