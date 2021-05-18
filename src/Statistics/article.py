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


