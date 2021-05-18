import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

from util import URL_Splitter , getID , ConvertDictValuesToInt , GetScore_BiggestWL , ParseTillSpace
from defs import *
from query import Query
import logging


def GetNews(limit=5):
	co = Options()
	co.add_argument("--headless")
	co.add_experimental_option("excludeSwitches", ["enable-logging"])
	
	driver = webdriver.Chrome(executable_path="chromedriver.exe" , options= co)
	tz_params = {'timezoneId': 'UTC'}
	driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
	driver.get("https://www.hltv.org/")
	soup = BeautifulSoup(driver.page_source , "html.parser")

	articles = soup.find_all("a" , {"class":"newsline article"})[:limit]
	news_articles = []
	for i in articles:
		news_articles.append(Query.Article(i.find("div" , {"class":"newstext"}).text , single=True))

	return news_articles


