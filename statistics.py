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



class TeamStats:
	@staticmethod
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


	@staticmethod
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

	@staticmethod
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

	@staticmethod
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


	@staticmethod
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


class PlayerStats:
    	
	@staticmethod
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
	

	@staticmethod
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

	
	@staticmethod
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

	@staticmethod
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

	@staticmethod
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

	@staticmethod
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


	@staticmethod
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
		


		



def GetArticleData(article:Article):
	co = Options()
	co.add_argument("--headless")
	co.add_experimental_option("excludeSwitches", ["enable-logging"])

	driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
	tz_params = {'timezoneId': 'UTC'}
	driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
	driver.get(article.href)
	soup = BeautifulSoup(driver.page_source , "html.parser")

	description = str((soup.find("p" , {"class":"headertext" , "itemprop":"description"}).text))
	time = soup.find("div" , {"class":"date"}).text.split("-")[len(soup.find("div" , {"class":"date"}).text.split("-"))-1][1:]

	try:
		event_name = soup.find("div" , {"class":"event text-ellipsis"}).a.text[1:]
		event_href = f'https://www.hltv.org{soup.find("div" , {"class":"event text-ellipsis"}).a.get("href")}'
		event_id = event_href.split("/")[len(event_href.split("/"))-2]
		event_logo = soup.find("div" , {"class":"event text-ellipsis"}).a.img.get("src")
		event = Event(name=event_name , id=event_id , href=event_href , logo=event_logo)
		article.data["event"] = event
	except:
		logging.info(f'{article} has no event object assigned.')
		

	if(article.title.startswith("Video: ")):
		video = soup.find("iframe" , {"class":"video"}).get("data-cookieblock-src")
		article.data["video"] = video


	article.data["description"] = description
	article.data["time"] = f'{time} UTC'
	driver.close()
	return article.data



shox = Query.Player("shox" , single=True)
print(shox)
print(PlayerStats.Clutches(shox))

xyp = Query.Player("xyp9x" , single=True)
print(xyp)
print(PlayerStats.Clutches(xyp))