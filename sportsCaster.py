import urllib.request, json, datetime, argparse
from twilio.rest import Client
from bs4 import BeautifulSoup
from dateutil import tz


#==============================================================================


# TWILIO ACCOUNT INFO - free sms gateway
TWILIO_PHONE =
ACCOUNT_SID  = 
AUTH_TOKEN   = 

# Target Phone Numbers
TARGET_PHONE = [
                # YOUR PHONE NUMBER HERE
               ]

# Club / Team / League Lists
ESPN_PAGE     = 'https://www.espn.com/soccer/scoreboard'

LEAGUES_CLUBS = {
                 'english-premier-league'   : ['Arsenal'],
                 'major-league-soccer'      : [],
                 'italian-serie-a'          : [],
                 'spanish-primera-division' : ['Barcelona'],
                 'mexican-ascenso-mx'       : [],
                 'dutch-eredivisie'         : [],
                 'international-friendly'   : []
                }

# ESPN ScoreBoard 
SCOREBOARD_STR      = 'window.espn.scoreboardData'
SCOREBOARD_SETT_STR = 'window.espn.scoreboardSettings'


#==============================================================================


def getScoreBoardJson(pageData):
    # scan all tags in the page to find the score board data
    for script in pageData.find_all('script'):
        if script.text.startswith(SCOREBOARD_STR,0,len(SCOREBOARD_STR)):
            scoreBoard = script
            break
    
    # the score board data contains the scoreboard data and the scoreboard
    # settings, filter out the settings
    startIndex = scoreBoard.text.find('{')
    stopIndex = scoreBoard.text.find(SCOREBOARD_SETT_STR) - 1
    
    # load the scoreboard data as a json and return it
    return json.loads(scoreBoard.text[startIndex : stopIndex])

def getLeagueName(league):
    leagueData = league['leagues']
    return leagueData[0]['slug'] # use the slug, since theirs issues with name

def getLeagues(allLeagues):
    leagues = []
    # loop through all leagues and see if it is a desired league
    for league in allLeagues:
        if getLeagueName(league) in LEAGUES_CLUBS:
            leagues.append(league)
    return leagues

def getMessageHeader():
    retStr  = '\n==========================\n'
    retStr += '   FIXTURES FOR %s\n' % (datetime.datetime.now().date())
    retStr += '==========================\n\n'
    return retStr

def getTeamsInGame(game):
    teams = []
    # loop through competitors in the game
    for team in game['competitions'][0]['competitors']: 
        teams.append(team['team']['shortDisplayName'])
    return teams

def isDesiredGame(game,leagueName):
    # see if the game includes a team that is in your desired teams list
    for team in getTeamsInGame(game):
        if team in LEAGUES_CLUBS[leagueName]:
            return True
    return False

def utcToMyTime(utc):
    # time zones
    utcTz = tz.gettz('UTC')
    myTz = tz.tzlocal()
    # get min and hour from game time
    utcHour = int(utc.split(':')[0])
    utcMin = int(utc.split(':')[1])
    #translate utc to your time zone
    utcTime = datetime.datetime.today().replace(hour=utcHour,minute=utcMin)
    utcTime = utcTime.replace(tzinfo=utcTz)
    myTime = utcTime.astimezone(myTz)
    return myTime.strftime('%I:%M %p')

def getTime(game):
    utcTime = game['competitions'][0]['date'][-6:].rstrip('Z')
    myTime = utcToMyTime(utcTime)
    return myTime 
    

def gameToString(game):
    teams = getTeamsInGame(game) # both teams competing 
    timeStr = getTime(game) # time of game
    return "%s VS %s (%s)\n" % (teams[0],teams[1],timeStr)

def leagueToString(league):
    desiredGames = 0 
    events = league['events'] # all of todays games/events in the league
    leagueStr = ''
    for game in events: # loop through all games
        # if the game has a desired team then build a string for it
        if isDesiredGame(game,getLeagueName(league)):
            leagueStr += gameToString(game)
            desiredGames += 1
            
    if desiredGames > 0: # league has desired games
        retStr  = getLeagueName(league).upper() + " :\n\n"
        retStr += leagueStr + "\n"
        retStr += '------------------------------------\n\n'
        return retStr
    else: # league has no desired games
        return ''

def scanEspn():
    # Retrieve site data 
    urlResponse = urllib.request.urlopen(ESPN_PAGE)
    rawHtml = urlResponse.read()
    pageData = BeautifulSoup(rawHtml,features="html.parser")
    
    # Get score board data as a json object
    scoreBoard = getScoreBoardJson(pageData)
    
    # Get list of desired leagues
    myLeagues = getLeagues(scoreBoard['scores'])
    
    # Build sms message
    message = ''
    message += getMessageHeader()
    for league in myLeagues: # put all my leagues into str
        message += leagueToString(league)
		
    if message == '': 
	    message = 'NO GAMES TODAY :('
        
    return message

def buildMessage(message):
    twilioCli = Client(ACCOUNT_SID,AUTH_TOKEN)
    sendMessage(twilioCli,message)

def sendMessage(client,msg):
    # send messgae to all phones
    for phones in TARGET_PHONE:
        client.messages.create(body=msg,from_=TWILIO_PHONE,to=phones)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-a',action='store_true',help='Enable afternoon mode')
	args = parser.parse_args()
	try:
		if args.a:
			message = 'FEATURE NOT YET IMPLENTED'
		else:
			message = scanEspn()
	except:
		message = 'ERROR: ESPN ScoreBoard could not be parsed'
		
	buildMessage(message)
    