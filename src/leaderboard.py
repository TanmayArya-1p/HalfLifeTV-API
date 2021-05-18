import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import requests

from util import URL_Splitter , getID , ConvertDictValuesToInt , GetScore_BiggestWL , ParseTillSpace
from defs import *

import logging


class TeamLeaderboard:

	@staticmethod
	def WorldRanking():
		co = Options()
		co.add_argument("--headless")
		co.add_experimental_option("excludeSwitches", ["enable-logging"])
		
		driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
		tz_params = {'timezoneId': 'UTC'}
		driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
		driver.get("https://www.hltv.org/ranking/teams")
		soup = BeautifulSoup(driver.page_source , "html.parser")
		header = soup.find("div" , {"class":"regional-ranking-header"}).text
		
		rankings = {}

		ranked_teams = soup.find("div" , {"class":"ranking"}).find_all("div" , {"class":"ranked-team standard-box"})
		for i in ranked_teams:
			data = {}
			position = int(i.find("span" , {"class":"position"}).text[1:])
			data["points"] = int(i.find("span" , {"class":"points"}).text[1:-8])

			team_name = i.find("span" , {"class":"name"}).text
			team_href = f'https://www.hltv.org{i.find("div" , {"class":"more"}).a.get("href")}'
			team_logo = i.find("span" , {"class":"team-logo"}).img.get("src")
			team_id = team_href.split("/")[len(team_href.split("/"))-2]
			data["team"] = Team(name=team_name , id=team_id , logo=team_logo , href=team_href)
			rankings[position] = data
		return rankings


	@staticmethod
	def GetRegions():
		co = Options()
		co.add_argument("--headless")
		co.add_experimental_option("excludeSwitches", ["enable-logging"])
		
		driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
		tz_params = {'timezoneId': 'UTC'}
		driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
		driver.get("https://www.hltv.org/ranking/teams")
		soup = BeautifulSoup(driver.page_source , "html.parser")

		regions = soup.find_all("div" , {"class":"ranking-country"}) 
		region_dict = {}
		for i in regions:
			region_dict[i.a.text] = f'https://www.hltv.org{i.a.get("href")}'
		continents = soup.find_all("span" , {"class":"ranking-region"}) 
		for i in continents:
			region_dict[i.a.text] = f'https://www.hltv.org{i.a.get("href")}'

		return region_dict


	@staticmethod
	def RegionRanking(region_href :str):
		if(region_href.startswith("https://www.hltv.org/ranking/teams")):
			try:
				co = Options()
				co.add_argument("--headless")
				co.add_experimental_option("excludeSwitches", ["enable-logging"])
				
				driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
				tz_params = {'timezoneId': 'UTC'}
				driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
				driver.get(region_href)
				soup = BeautifulSoup(driver.page_source , "html.parser")

				rankings = {}

				ranked_teams = soup.find("div" , {"class":"ranking"}).find_all("div" , {"class":"ranked-team standard-box"})
				for i in ranked_teams:
					data = {}
					position = int(i.find("span" , {"class":"position"}).text[1:])
					data["points"] = int(i.find("span" , {"class":"points"}).text[1:-8])

					team_name = i.find("span" , {"class":"name"}).text
					team_href = f'https://www.hltv.org{i.find("div" , {"class":"more"}).a.get("href")}'
					team_logo = i.find("span" , {"class":"team-logo"}).img.get("src")
					team_id = team_href.split("/")[len(team_href.split("/"))-2]
					data["team"] = Team(name=team_name , id=team_id , logo=team_logo , href=team_href)
					rankings[position] = data
					driver.close()
				return rankings
			except:
				raise AttributeError("Invalid Href")

		else:
			raise AttributeError("Invalid Href")



class PlayerLeaderboard:
	@staticmethod
	def AllTimeLeaderboard():
		co = Options()
		co.add_argument("--headless")
		co.add_experimental_option("excludeSwitches", ["enable-logging"])
		
		driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
		tz_params = {'timezoneId': 'UTC'}
		driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
		driver.get("https://www.hltv.org/stats/leaderboards")
		soup = BeautifulSoup(driver.page_source , "html.parser")

		cols = soup.find_all("div" , {"class":"col stats-rows"})
		otpt = {}
		for i in cols:
			boxes = i.find_all('div' , {"class":"standard-box"})
			headers = [j.span.a.text for j in i.find_all("div" , {"class" : None})] 
			for j in boxes:
				plyr_name = j.find('span' , {"class" : "leader-info-picture"}).img.get("title")
				plyr_href = f'https://www.hltv.org{j.find("span" , {"class":"leader-player"}).find("span" , {"leader-name"}).a.get("href")}'
				plyr_id = int(plyr_href.split("/")[len(plyr_href.split("/"))-2])
				plyr_country = j.find("span" , {"class":"leader-player"}).img.get("title")
				plyr_logo = j.find('span' , {"class" : "leader-info-picture"}).img.get("src")
				rating = j.find("span" , {"class" : "leader-rating"}).span.text
				curr = Player(name=plyr_name , id=plyr_id , country=plyr_country , logo=plyr_logo , href=plyr_href)

				otpt[headers[boxes.index(j)]] = [curr , rating]
		driver.close()
		return otpt
	

	@staticmethod
	def PlayersOfTheWeek():
		co = Options()
		#co.add_argument("--headless")
		co.add_experimental_option("excludeSwitches", ["enable-logging"])
		
		driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
		tz_params = {'timezoneId': 'UTC'}
		driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
		driver.get("https://www.hltv.org/")

		driver.find_element(By.XPATH , './/div[@class="playerOfTheWeekPlayerInfoContainer"]').click()
		soup = BeautifulSoup(driver.page_source , "html.parser")

		cols = soup.find_all("div" , {"class":"col stats-rows"})
		otpt = {}
		for i in cols:
			boxes = i.find_all('div' , {"class":"standard-box"})
			headers = [j.span.a.text for j in i.find_all("div" , {"class" : None})] 
			for j in boxes:
				plyr_name = j.find('span' , {"class" : "leader-info-picture"}).img.get("title")
				plyr_href = f'https://www.hltv.org{j.find("span" , {"class":"leader-player"}).find("span" , {"leader-name"}).a.get("href")}'
				plyr_id = int(plyr_href.split("/")[len(plyr_href.split("/"))-2])
				plyr_country = j.find("span" , {"class":"leader-player"}).img.get("title")
				plyr_logo = j.find('span' , {"class" : "leader-info-picture"}).img.get("src")
				rating = j.find("span" , {"class" : "leader-rating"}).span.text
				curr = Player(name=plyr_name , id=plyr_id , country=plyr_country , logo=plyr_logo , href=plyr_href)

				otpt[headers[boxes.index(j)]] = [curr , rating]
		driver.close()
		return otpt








