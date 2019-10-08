# SportsCaster
Get footy notifications about your favorite teams (via sms message)


## STEPS
### 1. TWILIO
This script uses TWILIO, a free sms-messaging gateway. Visit twilio.com, create an account, and get a twilio phone number! Once this is done, copy the twilio phone number, ACCOUNT SID, and AUTH TOKEN into the sportsCaster.py script.

### 2. ADD YOUR PHONE NUMBER
Add all phone numbers that you wish to receive footy notifications to the TARGET_PHONE list.

### 3. GET LEAGUE AND CLUB NAME
  1. Visit https://www.espn.com/soccer/scoreboard
  2. Hit ctrl+u to see the source code
  3. Search for 'slug' with ctrl+f to find leagues
  4. Look for a league that you wish to add the the LEAGUE_CLUBS dictionary by searching through the instances of 'slug'
  5. Add your league's slug value to the dictionary
  6. Search for 'shortDisplayName' with ctrl+f to find clubs
  7. Add club's shortDisplayName value to their appropriate leagues list
  
### 4. (OPTIONAL) FOR PI USERS
Automate notifications by using crontab -e 
  
## MESSAGES
### MORNING
In the morning the scripts sends the fixtures for the day and the time the games occur.
### AFTERNOON 
In the afternoon the script sends results of the games of that day
