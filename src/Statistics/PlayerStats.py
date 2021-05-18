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




def Overview(player:Player):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    player.data["Overview"] = {}
    
    #Age
    player.data["Overview"]["age"] = soup.find("div" , {"class":"summaryPlayerAge"}).text[:-6]
    #Stats Breakdown 
    for i in soup.find("div" , {"class":"summaryBreakdownContainer"}).find_all("div" , {"class":"summaryStatBreakdownRow"}):
        stats = [k for k in i.find_all("div") if (k.get("class")[:1] ==["summaryStatBreakdown"])]
        for j in stats:
            header=  j.find("div" , {"class":"summaryStatTooltip hiddenTooltip"}).b.text
            st = j.find("div" , {"class":"summaryStatBreakdownDataValue"}).text
            player.data["Overview"][header] = st
    #Stats Rows
    cols = [n for n in soup.find("div" , {"class":"statistics"}).div.find_all("div") if (n.get("class")[:1]==["col"])] 
    for i in cols:
        stats_rows = i.find_all("div" , {"class":"stats-row"})
        for stat_row in stats_rows:
            player.data["Overview"][stat_row.span.text] = stat_row.find_all("span")[1].text
    #Assigning Team Object:
    player.team = Query.Team(soup.find("img" , {"class":"team-logo"}).get("title") , single=True)
    
    player.data["Overview"] = ConvertDictValuesToInt(player.data["Overview"])
    return player.data["Overview"]


def Individual(player:Player):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/individual/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    player.data["Individual"] = {}

    #Iterating through columns
    cols = soup.find("div" , {"class":"statistics"}).div.find_all("div" , {"class":"col stats-rows"})
    for i in cols:
        headers = [header.span.text for header in i.find_all("div" , {"class":None})]
        boxes = i.find_all("div" , {"class":"standard-box"})
        for j in boxes:
            stats_rows = j.find_all("div" , {"class":"stats-row"})
            player.data["Individual"][headers[boxes.index(j)]] = {}
            for h in stats_rows:
                player.data["Individual"][headers[boxes.index(j)]][h.span.text] = h.find_all("span" , {"class":None})[len(h.find_all("span" , {"class":None}))-1].text
            player.data["Individual"][headers[boxes.index(j)]] = ConvertDictValuesToInt(player.data["Individual"][headers[boxes.index(j)]])
    
    return player.data["Individual"]



def Matches(player:Player , limit:int=3):
    co = Options()
    #co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/matches/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    player.data["Matches"] = {}
    rows = soup.find("table" , {"class":"stats-table no-sort"}).tbody.find_all("tr")
    l = 0
    match_history = []
    print("above loop")
    for i in rows:
        print("iterating")
        if(l == limit):
            break
        l += 1
        curr = {} 
        curr["date"] = f'{i.find("div" , {"class" : "time"}).text} UTC'
        

        t1_name = i.find_all("td")[1].find("div" , {"class":"text-center"}).img.get("title")
        t1_logo = i.find_all("td")[1].find("div" , {"class":"text-center"}).img.get("src")
        t1_href = f'https://www.hltv.org{i.find_all("td")[1].find_all("div")[1].a.get("href")}'
        t1_id = t1_href.split("/")[len(t1_href.split("/"))-2]
        t1_score = i.find_all("td")[1].find_all("div")[0].find_all('span')[1].text[2:-1]
        curr["T1"] = Team(name=t1_name , logo=t1_logo , href=t1_href , id=t1_id)

        t2_name = i.find_all("td")[2].find("div" , {"class":"text-center"}).img.get("title")
        t2_logo = i.find_all("td")[2].find("div" , {"class":"text-center"}).img.get("src")
        t2_href = f'https://www.hltv.org{i.find_all("td")[2].find_all("href")[1].a.get("href")}'
        t2_id = t2_href.split("/")[len(t2_href.split("/"))-2]
        t2_score = i.find_all("td")[2].find_all("div")[0].find_all('span')[1].text[2:-1]
        curr["T2"] = Team(name=t2_name , logo=t2_logo , href=t2_href , id=t2_id)
        curr["map"] = i.find("td" , {"class" : "statsMapPlayed"}).text
        curr["score"] = f"{t1_score}-{t2_score}"
        match_history.append(curr)
    player.data["Match History"] = match_history
    return  player.data["Match History"]


def EventHistory(player:Player , limit:int=3):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/events/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    headers = [i.text for i in soup.find("table" , {"class":"stats-table"}).thead.tr.find_all("th")]
    trs = soup.find("table" , {"class":"stats-table"}).tbody.find_all("tr")[:limit]
    event_his=[]
    for i in trs:
        curr = {}
        curr["placement"] = i.td.text
        t_href = f'https://www.hltv.org/team/{URL_Splitter(i.find("td" , {"class":"gtSmartphone-only"}).a.get("href"))}'
        curr["team"] = Team(name=i.find("td" , {"class":"smartphone-only text-center"}).img.get("title") , logo=i.find("td" , {"class":"smartphone-only text-center"}).img.get("src") , href= t_href, id=int(t_href.split("/")[len(t_href.split("/"))-2]))
        curr["event"] = Query.Event(i.find("img" , {"class":"eventLogo"}).get("title") , single=True)
        curr["Maps Played"] = i.find("td" , {"class":"statsMapPlayed"}).text

        rest_cols = i.find_all("td")[-3:]
        curr[headers[len(headers)-3]] = rest_cols[0].text
        curr[headers[len(headers)-2]] = rest_cols[1].text
        curr[headers[len(headers)-1]] = rest_cols[2].text
        curr = ConvertDictValuesToInt(curr)
        event_his.append(curr)

    player.data["Event History"] = event_his
    return event_his


def WeaponUsage(player:Player):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/weapon/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    driver.close()

    cols = soup.find("div" , {"class":"columns"}).find_all("div" , {"class":"col stats-rows standard-box"})
    otpt = {}
    for i in cols:
        rows = i.find_all("div" , {"class":"stats-row"})
        for k in rows:
            otpt[k.div.find_all("span")[1].text[1:]] = k.find_all("span")[len(k.find_all("span"))-1].text
    otpt = ConvertDictValuesToInt(otpt)
    return otpt

def Clutches(player:Player):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/clutches/{URL_Splitter(player.href).split("/")[0]}/1on1/{URL_Splitter(player.href).split("/")[1]}')
    WebDriverWait(driver,1).until(EC.visibility_of_element_located((By.ID , "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
    driver.find_element_by_id("CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()

    player.data["Clutches"] = {}
    soup = BeautifulSoup(driver.page_source , "html.parser")
    for g in range(0,5):			
        
        tabs = soup.find_all("div" , {"class":"stats-top-menu"})[1].find_all("div" , {"class":"tabs standard-box"})[1].find_all("a")
        i = tabs[g]
        driver.find_element_by_xpath("./"+xpath_soup(i)[10:]).click()
        soup = BeautifulSoup(driver.page_source , "html.parser")
        player.data["Clutches"][i.text] = {}

        for j in soup.find("div" , {"class":"summary"}).find_all("div" , {"class":"col"}):
            try:
                if(j.div.find("div" , {"class":"description"}).text[0] == " "):
                    player.data["Clutches"][i.text][j.div.find("div" , {"class":"description"}).text[1:]] = j.div.find("div" , {"class":"value"}).text
                else:
                    player.data["Clutches"][i.text][j.div.find("div" , {"class":"description"}).text] = j.div.find("div" , {"class":"value"}).text
                if(player.data["Clutches"][i.text]["Losses"] == '-'):
                    player.data["Clutches"][i.text]["Losses"] = "Not Recorded"
                player.data["Clutches"][i.text] = ConvertDictValuesToInt(player.data["Clutches"][i.text])
            except:
                pass

    return player.data["Clutches"]


def GetPlayerTeam(player:Player):
    co = Options()
    co.add_argument("--headless")
    co.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
    tz_params = {'timezoneId': 'UTC'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    driver.get(f'https://www.hltv.org/stats/players/{URL_Splitter(player.href)}')
    soup = BeautifulSoup(driver.page_source , "html.parser")
    player.team = Query.Team(soup.find("img" , {"class":"team-logo"}).get("title") , single=True)
    return player.team
