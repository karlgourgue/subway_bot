# subway_bot
Lola the NYC Subway Bot, a FB Messenger Bot that tells you more about the status of your subway.

Involves:
* Web-Scraping
* Python Flask
* Facebook Messenger API
* Building MySQL Database
* Visualization in Pandas

#### Problem
Many New Yorkers have trouble navigating the subway because of seemingly-random delays, planned work, and mechanical failures. Google Maps and related services are only sometimes accurate in displaying the status of trains. 

#### Defining Further
The biggest problem in determing status is access. Our team found that the faster you can see how a train is operating, the faster you can get to where you want to go. 

#### Difficulties
The initial challenge we faced was pulling the MTA's status information. This live data is notoriously tricky to connect to. Our workaround involved scraping the information online in intervals and storing the information in a MySQL DB. This solution gave us the opportunity to create additional metrics about the performance of our trains.

Another challenge was time. While we weren't able to include some planned features in the intial release, we had plans in place to produce:
* Automatic language translation
* Deeper data-sourced insights
* Train status prediction

#### Learning
Whereas we assumed that the data and information would be most important to the end-user, we realized the more important aspect of the project was speed. Users need to know this information *before* they begin their journeys, and finding ways to bring the information to them is half the challenge. 





Built off of Hung Tran's EchoBot
https://github.com/hungtraan/FacebookBot-echobot-simple
