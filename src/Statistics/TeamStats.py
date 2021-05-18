import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from util import URL_Splitter , getID , ConvertDictValuesToInt , GetScore_BiggestWL , ParseTillSpace , remove_non_ascii , xpath_soup
from defs import *
from query import Query
import logging



def GetTeamStats(team:Team):
	co = Options()
	co.add_argument("--headless")
	co.add_experimental_option("excludeSwitches", ["enable-logging"])
	
	#Gets World Ranking , weeks in top 30 , Avg Player Age , Coach , Players
	driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
	tz_params = {'timezoneId': 'UTC'}
	driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
	driver.get(team.href)

	soup = BeautifulSoup(driver.page_source , "html.parser")
	st1 = soup.find_all("div" , {"class":"profile-team-stat"})
	for i in st1:
		if(i.find("span" , {"class":"right"}) != None):
			team.data[i.b.text] = i.span.text
		else:
			team.data[i.b.text] = Player(name=i.a.text , id=i.a.get("href").split("/")[len(i.a.get("href").split("/"))-2] , logo = f'https://www.hltv.org{i.a.img.get("src")}' , href = f'https://www.hltv.org{i.a.get("src")}' , country=i.a.img.get("title"))
	#Iterating through players.
	plyrs = soup.find_all("a" , {"class" : "col-custom"})
	plyr_list = []
	for i in plyrs:
		pname = i.img.get("title")
		plogo = i.img.get("src")
		phref = f'https://www.hltv.org{i.get("href")}'
		pid = phref.split("/")[len(phref.split("/"))-2]
		pcountry = i.find("img" , {"class":"flag"}).get("title")
		pcurr = Player(name = pname , id= pid , href=phref , logo = plogo , country = pcountry)
		plyr_list.append(pcurr)
	team.data["Players"] = plyr_list
	driver.close()
	#stats_href = f'https://www.hltv.org{soup.find("div" , {"id" : "statsBox"}).find("a" , {"class" : "moreButton"}).get("href")}'
	stats_href = f'https://www.hltv.org/stats/teams/{URL_Splitter(team.href)}'
	#Scraping Overview Statistics Page.
	driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
	driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
	driver.get(stats_href)
	soup = BeautifulSoup(driver.page_source , "html.parser")
	overview_cols = soup.find_all("div" , {"class" : "columns"})
	for i in overview_cols:
		col_boxes = i.find_all("div" , {"class":"col standard-box big-padding"})
		for j in col_boxes:
			team.data[j.find_all("div")[1].text] = j.find_all("div")[0].text
	#Player Grids:
	maps_played = {}
	plyr_grps = soup.find_all("div" , {"class" : "grid reset-grid"})
	for i in plyr_grps:
		for j in i.find_all("div"):
			if(("teammate" in j.get("class")) and not("no-height" in j.get("class"))):
				try:
					pname = j.find("img" , {"class":"ccontainer-width teammate-player-image disabled-img"}).get("title")
					plogo = j.find("img", {"class":"container-width teammate-player-image disabled-img"}).get("src")
				except:
					pname = j.find("img").get("title")
					plogo = j.find("img").get("src")
				phref =  f'https://www.hltv.org/team/{URL_Splitter(j.find("a").get("href"))}'
				pid = getID(phref)
				pcountry = j.find("a").find("img" , {"class":"flag"}).get("title")
				curr = Player(name = pname , id= pid , href=phref , logo = plogo , country = pcountry)
				maps_played[curr] = j.find("span").text
	driver.close()
	team.data["Maps Played"] = maps_played
	
	#Opening Match Tab:
	driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
	tz_params = {'timezoneId': 'UTC'}
	driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
	driver.get(f'https://www.hltv.org/stats/teams/matches/{URL_Splitter(team.href)}')
	soup = BeautifulSoup(driver.page_source , "html.parser")
	rows = soup.find("tbody").find_all("tr")
	l = 0
	match_history = []
	for i in rows:
		if(l == 10):
			break
		l += 1
		curr = {} 
		curr["date"] = i.find("td" , {"class" : "time"}).a.text
		curr["event"] = Query.Event(str(i.find("span").text) , single=True)
		curr["T2"] = Query.Team(str(i.find_all("td")[3].a.text) , single=True)
		curr["T1"] = team
		curr["map"] = i.find("td" , {"class" : "statsMapPlayed"}).span.text
		curr["score"] = i.find_all("td")[5].span.text
		handler = CompletedMap(t1=curr["T1"] ,t2=curr["T2"] ,m_map=curr["map"] ,score=curr["score"] ,mevent=curr["event"] , date=curr["date"])
		match_history.append(handler)
	team.data["Match History"] = match_history

	return (team.data)




def MatchHistory(team:Team , limit:int = 3 ):
    #Opening Match Tab:
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/teams/matches/{URL_Splitter(team.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    rows = soup.find("tbody").find_all("tr")
    l = 0
    match_history = []
    for i in rows:
        if(l == limit):
            break
        l += 1
        curr = {} 
        curr["date"] = f'{i.find("td" , {"class" : "time"}).a.text} UTC'
        curr["event"] = Query.Event(str(i.find("span").text) , single=True)
        curr["T2"] = Query.Team(str(i.find_all("td")[3].a.text) , single=True)
        curr["T1"] = team
        curr["map"] = i.find("td" , {"class" : "statsMapPlayed"}).span.text
        curr["score"] = f'{i.find_all("td")[5].span.text.split(" - ")[0]}-{i.find_all("td")[5].span.text.split(" - ")[1]}'
        handler = CompletedMap(t1=curr["T1"] ,t2=curr["T2"] ,m_map=curr["map"] ,score=curr["score"] ,mevent=curr["event"] , date=curr["date"])
        match_history.append(handler)
    team.data["Match History"] = match_history
    driver.close()
    return team.data["Match History"]



def Overview(team:Team):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])
    team.data["Overview"] = {}
    
    #Gets World Ranking , weeks in top 30 , Avg Player Age , Coach , Players
    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(team.href)

    soup = BeautifulSoup(driver.page_source , "html.parser")
    st1 = soup.find_all("div" , {"class":"profile-team-stat"})
    for i in st1:
        if(i.find("span" , {"class":"right"}) != None):
            team.data["Overview"][i.b.text] = i.span.text
        else:
            team.data["Overview"][i.b.text] = Player(name=i.a.text , id=int(i.a.get("href").split("/")[len(i.a.get("href").split("/"))-2]) , href = f'https://www.hltv.org{i.a.get("href")}' , country=i.a.img.get("title"))

    #Iterating through players.
    plyrs = soup.find_all("a" , {"class" : "col-custom"})
    plyr_list = []
    for i in plyrs:
        pname = i.img.get("title")
        plogo = i.img.get("src")
        phref = f'https://www.hltv.org{i.get("href")}'
        pid = phref.split("/")[len(phref.split("/"))-2]
        pcountry = i.find("img" , {"class":"flag"}).get("title")
        pcurr = Player(name = pname , id= pid , href=phref , logo = plogo , country = pcountry)
        plyr_list.append(pcurr)
    team.data["Overview"]["Players"] = plyr_list
    driver.close()
    #stats_href = f'https://www.hltv.org{soup.find("div" , {"id" : "statsBox"}).find("a" , {"class" : "moreButton"}).get("href")}'
    stats_href = f'https://www.hltv.org/stats/teams/{URL_Splitter(team.href)}'
    #Scraping Overview Statistics Page.
    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(stats_href)
    soup = BeautifulSoup(driver.page_source , "html.parser")
    overview_cols = soup.find_all("div" , {"class" : "columns"})
    for i in overview_cols:
        col_boxes = i.find_all("div" , {"class":"col standard-box big-padding"})
        for j in col_boxes:
            team.data["Overview"][j.find_all("div")[1].text] = j.find_all("div")[0].text
    driver.close()
    return team.data["Overview"]


def RosterHistory(team:Team):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    stats_href = f'https://www.hltv.org/stats/teams/{URL_Splitter(team.href)}'
    driver.get(stats_href)
    soup = BeautifulSoup(driver.page_source , "html.parser")

    #Player Grids:
    maps_played = {}
    plyr_grps = soup.find_all("div" , {"class" : "grid reset-grid"})
    for i in plyr_grps:
        for j in i.find_all("div"):
            if(("teammate" in j.get("class")) and not("no-height" in j.get("class"))):
                try:
                    pname = j.find("img" , {"class":"ccontainer-width teammate-player-image disabled-img"}).get("title")
                    plogo = j.find("img", {"class":"container-width teammate-player-image disabled-img"}).get("src")
                except:
                    pname = j.find("img").get("title")
                    plogo = j.find("img").get("src")
                phref =  f'https://www.hltv.org/team/{URL_Splitter(j.find("a").get("href"))}'
                pid = getID(phref)
                pcountry = j.find("a").find("img" , {"class":"flag"}).get("title")
                curr = Player(name = pname , id= pid , href=phref , logo = plogo , country = pcountry)
                maps_played[curr] = j.find("span").text
    driver.close()
    team.data["Roster History"] = maps_played
    return team.data["Roster History"]


def Maps(team:Team):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    map_href = f'https://www.hltv.org/stats/teams/maps/{URL_Splitter(team.href)}'
    driver.get(map_href)
    soup = BeautifulSoup(driver.page_source , "html.parser")
    cols = soup.find("div" , {"class" : "stats-section stats-team stats-team-maps"}).find("div" , {"class" : "two-grid"}).find_all("div" , {"class" : "col"})
    
    print(cols)
    otpt = {}
    for i in cols:
        try:
            map_name = i.find("div" , {"class":"map-pool"}).a.div.div.text
            stats_rows = i.find_all("div" , {"class":"stats-row"})
            map_otpt = {}
            #Gets Stats of Maps
            for j in stats_rows:
                map_otpt[j.find_all("span")[0].text] = j.find_all("span")[1].text

            win_defeat = i.find("div" , {"class" :"two-grid win-defeat-container"}).find_all("div" , {"class":"col"})
            for j in win_defeat:
                header = j.a.find_all("div")[1].div.text
                score = j.a.find_all("div")[1].find_all("div")[1].text
                match_id = j.a.get("href").split("/")[len(j.a.get("href").split("/"))-2]
                map_otpt[header] = [int(match_id) , (score)]
            map_otpt = ConvertDictValuesToInt(map_otpt)
            otpt[map_name] = map_otpt
        except:
            pass

    team.data["Maps"] = otpt
    driver.close()
    return team.data["Maps"]



def EventHistory(team:Team , limit=5):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    event_href = f'https://www.hltv.org/stats/teams/events/{URL_Splitter(team.href)}'
    driver.get(event_href)
    soup = BeautifulSoup(driver.page_source , "html.parser")
    rows = soup.find("table" , {"class":"stats-table"}).tbody.find_all("tr")
    history = []
    it = 0 
    for i in rows:
        if(it == limit):
            break
        otpt = {}
        otpt["placement"] = i.td.text
        otpt["event"] = Query.Event(str(i.a.span.text) , single=True)
        otpt["team"] = team
        print(otpt)
        history.append(otpt)
        it += 1
    driver.close()
    return history