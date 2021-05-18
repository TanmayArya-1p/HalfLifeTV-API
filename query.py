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
import datetime

from defs import Team , Player , Event , Article , UpcomingMatch , CompletedMap , LiveMatch
from util import URL_Splitter , getID


class Query:

	@staticmethod
	def Team(team:str , drv:webdriver.Chrome = None , single=False):
		if(drv == None):
			co = Options()
			co.add_experimental_option("excludeSwitches", ["enable-logging"])
			co.add_argument("--headless")

			driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
			tz_params = {'timezoneId': 'UTC'}
			driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
			driver.get(f"https://www.hltv.org/search?query={team}")
		else:
			driver = drv
		soup = BeautifulSoup(driver.page_source , "html.parser")

		tables = soup.find_all("table" , {"class" : "table"})

	
		#Filterer:
		results = {}
		for i in tables:
			results[i.tbody.tr.td.text] = i

		if(single):
			if("Team" in list(results.keys())):
				i = results.get("Team").tbody.find_all("tr")[1:][0]
				tn = (i.td.a.img.get("title"))
				thref = f'https://www.hltv.org{i.td.a.get("href")}'
				tlogo = i.td.a.img.get("src")
				tid = int(thref.split("/")[len(thref.split("/"))-2])
				curr = Team(name=tn , href=thref , logo=tlogo , id= tid)
			if(drv == None):
				driver.close()
			return curr
		else:
			q = []
			if("Team" in list(results.keys())):
				items = results.get("Team").tbody.find_all("tr")[1:]
				for i in items:
					tn = (i.td.a.img.get("title"))
					thref = f'https://www.hltv.org{i.td.a.get("href")}'
					tlogo = i.td.a.img.get("src")
					tid = int(thref.split("/")[len(thref.split("/"))-2])
					curr = Team(name=tn , href=thref , logo=tlogo , id= tid)
					q.append(curr)
			if(drv == None):
				driver.close()
			return q


	@staticmethod
	def Player(plyr:str , drv:webdriver.Chrome = None , single=False):
		if(drv == None):
			co = Options()
			co.add_experimental_option("excludeSwitches", ["enable-logging"])
			co.add_argument("--headless")

			driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
			tz_params = {'timezoneId': 'UTC'}
			driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
			driver.get(f"https://www.hltv.org/search?query={plyr}")
		else:
			driver = drv
		soup = BeautifulSoup(driver.page_source , "html.parser")

		tables = soup.find_all("table" , {"class" : "table"})

		
		#Filterer:
		results = {}
		for i in tables:
			results[i.tbody.tr.td.text] = i

		if(single):
			if("Player" in list(results.keys())):
				
				i = results.get("Player").tbody.find_all("tr")[1:][0]

				pn = (i.td.a.text)
				phref = f'https://www.hltv.org{i.td.a.get("href")}'
				plogo = f'https://www.hltv.org{i.td.a.img.get("src")}'
				pid = int(phref.split("/")[len(phref.split("/"))-2])
				pflag = i.td.a.img.get("title")
				curr = Player(name=pn , href=phref , logo=plogo , id= pid , country=pflag)
			
			if(drv == None):
				driver.close()
			return curr

		else:
			q = []
			if("Player" in list(results.keys())):
				
				items = results.get("Player").tbody.find_all("tr")[1:]
				for i in items:
					pn = (i.td.a.text)
					phref = f'https://www.hltv.org{i.td.a.get("href")}'
					plogo = f'https://www.hltv.org{i.td.a.img.get("src")}'
					pid = int(phref.split("/")[len(phref.split("/"))-2])
					pflag = i.td.a.img.get("title")
					curr = Player(name=pn , href=phref , logo=plogo , id= pid , country=pflag)
					q.append(curr)
			if(drv == None):
				driver.close()
			return q


	@staticmethod
	def Event(evnt:str , drv:webdriver.Chrome = None , single=True):
		if(drv == None):
			co = Options()
			co.add_experimental_option("excludeSwitches", ["enable-logging"])
			co.add_argument("--headless")

			driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
			tz_params = {'timezoneId': 'UTC'}
			driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
			driver.get(f"https://www.hltv.org/search?query={evnt}")
		else:
			driver = drv
		soup = BeautifulSoup(driver.page_source , "html.parser")

		tables = soup.find_all("table" , {"class" : "table"})

		
		#Filterer:
		results = {}
		for i in tables:
			results[i.tbody.tr.td.text] = i
		
		if(single):
			if("Event" in list(results.keys())):
				i = results.get("Event").tbody.find_all("tr")[1:][0]
				en = (i.td.a.text)
				ehref = f'https://www.hltv.org{i.td.a.get("href")}'
				elogo = i.td.a.img.get("src")
				eid = int(ehref.split("/")[len(ehref.split("/"))-2])
				curr = Event(name=en , href=ehref , logo=elogo , id= eid)
			if(drv == None):
				driver.close()
			return curr
		else:
			q = []
			if("Event" in list(results.keys())):
				items = results.get("Event").tbody.find_all("tr")[1:]
				for i in items:
					en = (i.td.a.text)
					ehref = f'https://www.hltv.org{i.td.a.get("href")}'
					elogo = i.td.a.img.get("src")
					eid = int(ehref.split("/")[len(ehref.split("/"))-2])
					curr = Event(name=en , href=ehref , logo=elogo , id= eid)
					q.append(curr)
			if(drv == None):
				driver.close()
			return q

	@staticmethod
	def Article(artcl:str , drv:webdriver.Chrome = None , single=False):
		if(drv == None):
			co = Options()
			co.add_experimental_option("excludeSwitches", ["enable-logging"])
			co.add_argument("--headless")

			driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
			tz_params = {'timezoneId': 'UTC'}
			driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
			driver.get(f"https://www.hltv.org/search?query={artcl}")
		else:
			driver = drv
		soup = BeautifulSoup(driver.page_source , "html.parser")

		tables = soup.find_all("table" , {"class" : "table"})

		
		#Filterer:
		results = {}
		for i in tables:
			results[i.tbody.tr.td.text] = i

		if(single):
			if("Article" in list(results.keys())):
				i = results.get("Article").tbody.find_all("tr")[1:][0]

				an = (i.td.a.text)
				ahref = f'https://www.hltv.org{i.td.a.get("href")}'
				alogo = i.td.a.img.get("title")
				aid = int(ahref.split("/")[len(ahref.split("/"))-2])
				aauthor = i.find_all("a")[1].text
				adate = f'{i.find("td" , {"class":"text-center search-date"}).span.text} UTC'
				curr = Article(title=an , href=ahref , country=alogo , id= aid , date=adate , author=aauthor)
	
			if(drv == None):
				driver.close()
			return curr
		else:
			q = []
			if("Article" in list(results.keys())):
				items = results.get("Article").tbody.find_all("tr")[1:]
				for i in items:
					an = (i.td.a.text)
					ahref = f'https://www.hltv.org{i.td.a.get("href")}'
					alogo = i.td.a.img.get("title")
					aid = int(ahref.split("/")[len(ahref.split("/"))-2])
					aauthor = i.find_all("a")[1].text
					adate = f'{i.find("td" , {"class":"text-center search-date"}).span.text} UTC'
					curr = Article(title=an , href=ahref , country=alogo , id= aid , date=adate , author=aauthor)
					q.append(curr)
			if(drv == None):
				driver.close()
			return q


	@staticmethod
	def Search(q:str):
		co = Options()
		co.add_experimental_option("excludeSwitches", ["enable-logging"])
		co.add_argument("--headless")

		driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
		tz_params = {'timezoneId': 'UTC'}
		driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
		driver.get(f"https://www.hltv.org/search?query={q}")
		Events = Query.Event(q , drv=driver)
		Players = Query.Player(q , drv=driver)
		Teams = Query.Team(q , drv=driver)
		Articles = Query.Article(q , drv=driver)
		driver.close()
		return {"Events" : Events , "Players" : Players , "Teams" : Teams , "Articles" : Articles}


def CompleteData(obj):
	if(type(obj) == Event):
		temp_data = obj.data
		r = Query.Event(str(obj.name) , single=True)
		r.data = temp_data
		return r
	elif(type(obj) == Player):
		temp_data = obj.data
		r = Query.Player(str(obj.name) , single=True)
		r.data = temp_data
		return r
	elif(type(obj) == Team):
		temp_data = obj.data
		r = Query.Team(str(obj.name) , single=True)
		r.data = temp_data
		return r
	elif(type(obj) == Article):
		temp_data = obj.data
		r = Query.Article(str(obj.name) , single=True)
		r.data = temp_data
		return r
	elif(type(obj) == UpcomingMatch):
		t1 = CompleteData(obj.t1)
		obj.t1 = t1
		t2 = CompleteData(obj.t2)
		obj.t2=t2
		ev = CompleteData(obj.event)
		obj.event= ev
		return obj
	elif(type(obj) == LiveMatch):
		t1 = CompleteData(obj.t1)
		obj.t1 = t1
		t2 = CompleteData(obj.t2)
		obj.t2=t2
		ev = CompleteData(obj.event)
		obj.event= ev
		obj.set_status()
		return obj
	
	else:
		AttributeError("'obj' must be of type Player,Event,Article,UpcomingMatch,CompletedMap,LiveMatch.")




