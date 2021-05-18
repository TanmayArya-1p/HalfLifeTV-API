import requests
from bs4 import BeautifulSoup
import os
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

from defs import *
from query import Query , CompleteData
from util import Capitalize




def GetUpcomingMatchesJSON(limit:int = None):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get("https://www.hltv.org/matches")

    time.sleep(2)
    upcoming_matches_soup = BeautifulSoup(driver.page_source , "html.parser").find("div" , {"class":"upcomingMatchesContainer"}).find_all("div" , {"class" : "upcomingMatchesSection"})
    
    match_dict = {}
    match_count = 0
    for i in (upcoming_matches_soup):
        #Iterating through UpcomingMatchesSection
        
        section_dict = {}
        section_match_list =[]

        #Headline of UpcomingMatchesSection (Day and Date)
        headline = f'{i.find("div" , {"class" : "matchDayHeadline"}).text} UTC'

        for f in i.find_all("div"):
            if((limit != None) and (match_count == limit)):
                break

            #Interating through Matches
            if(str(f.get("class")[0]).startswith("upcomingMatch")):
                #List of Elements with teams as text
                team_list = f.find_all("div" , {"class" : "matchTeamName text-ellipsis"})

                #Gets Event Name (Eg.ESL Pro League 13)
                for h in f.find_all("div"):
                    if(h.get("class")[0].startswith("matchEventName")):
                        event = (h.text)
                        break
                #Gets type of match (b01,b03,b05)
                meta =  f.find("div" , {"class" : "matchMeta"}).text
                #Get UTC time of Match
                t = f'{f.find("div" , {"class" : "matchTime"}).text} UTC'
                #Gets href of HLTV analytics of a match
                try:
                    analytics = f'https://www.hltv.org{f.find("a" , {"class" : "matchAnalytics"}).get("href")}'
                except:
                    analytics = ""
                #Appends match to section list
                if(len(team_list) == 2):
                    section_match_list.append({"T1" : team_list[0].text, "T1-ID" : int(f.get("team1")) , "T2": team_list[1].text , "T2-ID" : int(f.get("team2")) ,"event" : event ,"time" : t,"href" : f'https://www.hltv.org{f.find("a").get("href")}' , "LAN" : bool(Capitalize(f.get("lan"))) , "format" : meta , "analytics-href" : analytics , "stars" : int(f.get("stars"))})
                    match_count += 1

        if(len(section_match_list) != 0):
            match_dict[headline] = section_match_list
        if((limit != None) and (match_count == limit)):
            break
    driver.close()
    return match_dict

def GetUpcomingMatches(limit:int=None):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get("https://www.hltv.org/matches")

    time.sleep(2)
    upcoming_matches_soup = BeautifulSoup(driver.page_source , "html.parser").find("div" , {"class":"upcomingMatchesContainer"}).find_all("div" , {"class" : "upcomingMatchesSection"})
    
    match_dict = {}
    match_count = 0
    for i in (upcoming_matches_soup):
        #Iterating through UpcomingMatchesSection
        
        section_dict = {}
        section_match_list =[]

        #Headline of UpcomingMatchesSection (Day and Date)
        headline = f'{i.find("div" , {"class" : "matchDayHeadline"}).text} UTC'

        for f in i.find_all("div"):
            if((limit != None) and (match_count == limit)):
                break

            #Interating through Matches
            if(str(f.get("class")[0]).startswith("upcomingMatch")):
                #List of Elements with teams as text
                team_list = f.find_all("div" , {"class" : "matchTeamName text-ellipsis"})

                #Gets Event Name (Eg.ESL Pro League 13)
                for h in f.find_all("div"):
                    if(h.get("class")[0].startswith("matchEventName")):
                        event = (h.text)
                        break
                #Gets type of match (b01,b03,b05)
                meta =  f.find("div" , {"class" : "matchMeta"}).text
                #Get UTC time of Match
                t = f'{f.find("div" , {"class" : "matchTime"}).text} UTC'
                #Gets href of HLTV analytics of a match
                try:
                    analytics = f'https://www.hltv.org{f.find("a" , {"class" : "matchAnalytics"}).get("href")}'
                except:
                    analytics = ""
                #Appends match to section list
                if(len(team_list) == 2):
                    section_match_list.append(UpcomingMatch(Team1=Team(name=(team_list[0].text)) , Team2=Team(name=(team_list[1].text))  , event=Event(name=event) , time=t , href= f'https://www.hltv.org{f.find("a").get("href")}' , lan=bool(Capitalize(f.get("lan"))) , format=meta , analytics_href=analytics , stars= int(f.get("stars"))))
                    match_count += 1

        if(len(section_match_list) != 0):
            match_dict[headline] = section_match_list
        if((limit != None) and (match_count == limit)):
            break
    driver.close()
    return match_dict




def GetLiveMatchesJSON():
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get("https://www.hltv.org/matches")

    match_list = []

    soup = BeautifulSoup(driver.page_source , "html.parser")
    live_matches = soup.find("div" , {"class" : "liveMatches"}).find_all("div" , {"class" : "liveMatch-container"})

    for i in live_matches:
        #List of Elements with teams as text
        team_list = i.find_all("div" , {"class" : "matchTeamName text-ellipsis"})
        #Gets Event Name (Eg.ESL Pro League 13)
        for h in i.find("div" , {"class": "liveMatch"}).find_all("div"):
            if("matchEventName" in h.get("class")):
                event = (h.text)
                break
        #Gets Score
        score_elements = i.find_all('div' , {"class" : "matchTeamScore"})
        s1 = int(score_elements[0].span.text[1:])
        s2 = int(score_elements[1].span.text[1:])
   
        maps_1 = (score_elements[0].find("span" , {"class" : "mapScore"}).span.text)
        maps_2 = (score_elements[1].find("span" , {"class" : "mapScore"}).span.text)
        score = f'{s1}-{s2}'
        s = (maps_1,maps_2)

        #Gets type of match (b01,b03,b05)
        meta =  i.find("div" , {"class" : "matchMeta"}).text
        #Gets href of HLTV analytics of a match
        try:
            analytics = f'https://www.hltv.org{i.find("a" , {"class" : "matchAnalytics"}).get("href")}'
        except:
            analytics = ""
        #maps
        maps = i.get("data-maps")
        if(len(team_list) == 2):
            match_list.append({"T1" : team_list[0].text , "T1-ID" : int(i.get("team1")) , "T2" :team_list[1].text , "T2-ID" :  int(i.get("team2")) , "event" : event, "LAN" :  bool(Capitalize(i.get("lan"))) , "maps" : maps  , "href":f'https://www.hltv.org{i.find("a").get("href")}', "format" : meta , "analytics-href" : analytics , "stars" : int(i.get("stars")) , "score" : (score,s)})
    driver.close()
    return match_list



def GetLiveMatches():
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get("https://www.hltv.org/matches")

    match_list = []
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source , "html.parser")
    live_matches = soup.find("div" , {"class" : "liveMatches"}).find_all("div" , {"class" : "liveMatch-container"})

    for i in live_matches:
        #List of Elements with teams as text
        team_list = i.find_all("div" , {"class" : "matchTeamName text-ellipsis"})
        #Gets Event Name (Eg.ESL Pro League 13)
        for h in i.find("div" , {"class": "liveMatch"}).find_all("div"):
            if("matchEventName" in h.get("class")):
                event = (h.text)
                break
        #Gets Score
        score_elements = i.find_all('div' , {"class" : "matchTeamScore"})
        s1 = int(score_elements[0].span.text[1:])
        s2 = int(score_elements[1].span.text[1:])
   
        maps_1 = (score_elements[0].find("span" , {"class" : "mapScore"}).span.text)
        maps_2 = (score_elements[1].find("span" , {"class" : "mapScore"}).span.text)
        score = f'{s1}-{s2}'
        s = (maps_1,maps_2)

        #Gets type of match (b01,b03,b05)
        meta =  i.find("div" , {"class" : "matchMeta"}).text
        #Gets href of HLTV analytics of a match
        try:
            analytics = f'https://www.hltv.org{i.find("a" , {"class" : "matchAnalytics"}).get("href")}'
        except:
            analytics = ""
        #maps
        maps = i.get("data-maps")
        if(len(team_list) == 2):
            match_list.append(LiveMatch(Team1=Team(name=team_list[0].text) , Team2=Team(name=team_list[1].text) , href=f'https://www.hltv.org{i.find("a").get("href")}' , maps=maps , lan=bool(Capitalize(i.get("lan"))) , format=meta , stars=  int(i.get("stars")) , event=Event(name=event) , analytics_href = analytics , score=(score , s) ))
    driver.close()
    return match_list
