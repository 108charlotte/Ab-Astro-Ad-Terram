# text_adventure_game
This is my second attempt at a flask-based text adventure game, this time using SQL! 

### live link: (https://108charlotte.pythonanywhere.com/)
* if you don't see anything for a second or it doesn't look like it populated right, just reload the page! also, since this application is built on sqlite, every time the flask app is re-initialized the database is reset too, so your data is not saved permanently--although this is a feature I may work on in the future, it is not my main goal at the moment! 

## why i made it
I wanted to create a text adventure game since my last attempt didn't live up to my expectations. Although I had tried to make it scalable for adding more to the map, I hadn't considered that multiple users would have to use it at once and had to haphazardly implement it. After doing so, my processing was remarkably slow. This time, I decided to build my game logic on a SQL database using SQLite so that it could more easily handle the large amounts of data that I need it to in order to build a comprehensive world. Ultimately, I wanted to try my hand at the same task as when I had first started programming and see if I had improved (and I certainly did)! 

## how i made it
This is a flask-based application hosted on railway and using SQLite for the backend. I took a lot of inspiration and learned a lot from my last attempt at my text adventure game, which inspired the original idea for the game. Structure-wise, I added basic files to the root directory like my README.md, .gitignore, requirements.txt, etc. I also have two directories--a virtual environment, and a flask app. Inside of the flask app, I am using a factory pattern to create my app. Also directly inside of my app, I have a simple todo.md file to keep track of my tasks related to the app, a schema.sql for database initialization, and a db.py which populates the database with all the necessary information (see reset-db). I also have a game blueprint where the actual game logic and processing goes--most of it goes on in the utils file, but the routes.py file handles actually serving the data to the html template. I deployed on railway, since I had deployed my last text adventure game on render and it was far too slow and annoying to use. 

## challenges
This time I committed to using less AI assistance and programming the majority of it on my own. While this certainly led to a lot of annoyance and what felt like wasted time, in hidinsight I learned a lot about programming and reasoning through those annoying bugs was definitely worth it in the end. I feel like I have created something on my own and I am so proud of it and grateful for the amazing experience! 

## what's next? 
I hope to develop an engaging story centered around adventure! Most of this will occur in the db.py file in the reset-db function, but if I ever want to add extra functionality I will also have to update schema.sql and utils.py, so keep an eye on those! Another big issue is that, since everything is hosted on sqlite, users' data is not saved when the flask app is reinitialized. Fixing this by transferring the app over to another backend or switching to Postgre is not currently one of my goals, but maybe at some point in the future I will return to implement it! 

## an extra note
This project is being submitted for hack club's shipwrecked event, where qualifiers get to attend a 4-day hackathon on Cathleen Stone Island in Boston harbor in early August! 

<div align="center">
  <a href="https://shipwrecked.hackclub.com/?t=ghrm" target="_blank">
    <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/739361f1d440b17fc9e2f74e49fc185d86cbec14_badge.png" 
         alt="This project is part of Shipwrecked, the world's first hackathon on an island!" 
         style="width: 35%;">
  </a>
</div>
