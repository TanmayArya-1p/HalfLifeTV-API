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

from util import *


#Event Object		
class Event(AutoRepr):
	def __init__(self,name:str , href:str=None , id:int=None, logo:str="" ):
		self.name = name
		self.href = href
		self.logo = logo
		self.id = id
		self.data = {}

#Team Object
class Team(AutoRepr):
	def __init__(self , name:str , id:int=0 , href:str="", logo:str="" ):
		self.name = name
		self.id = id
		self.logo = logo
		self.href = href
		self.data = {}


#Upcoming Match Object
class UpcomingMatch(AutoRepr):

	def __init__(self, Team1:Team , Team2:Team ,  href:str ,lan:bool , format:str , event:Event=None , time:str="" ,  analytics_href:str="" , stars:int=0 ):
		self.t1 = Team1
		self.t2 = Team2
		self.event = event
		self.time = time
		self.href = href
		self.lan = lan
		self.frmt = format
		self.analytics_href = analytics_href
		self.stars = stars
		self.data={}


#Live Match Object
class LiveMatch(AutoRepr):
	def __init__(self, Team1:Team , Team2:Team  ,  href:str,  format:str ,event:Event=None  , maps:str="TBA" , stars:int=0 , lan:bool=False , analytics_href:str="" , score:tuple=""):
		self.t1 = Team1
		self.t2 = Team2
		self.event = event
		self.href = href
		self.lan = lan
		self.frmt = format
		self.maps = maps
		self.stars = stars
		self.score = score
		self.set_status()
	
	def set_status(self):
		if(self.score[1][0] > self.score[1][1]):
			self.winning = self.t1
			self.losing = self.t2
		elif(self.score[1][0] < self.score[1][1]):
			self.winning = self.t2
			self.losing = self.t1
		else:
			if(self.score[0].split("-")[0] > self.score[0].split("-")[1]):
				self.winning = self.t1
				self.losing = self.t2
			else:
				self.winning = self.t2
				self.losing = self.t1



#Player Object
class Player(AutoRepr):
	def __init__(self , name:str , id:int=0 ,  href:str="", logo:str=""  , country:str="" , team:Team=None):
		self.name = name
		self.id = id
		self.logo = logo
		self.href = href
		self.country = country
		self.team=team
		self.data= {}


#Article Object
class Article(AutoRepr):
	def __init__(self,title:str , href:str="" , id:int=0, author:str="" , date:str="", country:str=""):
		self.title = title
		self.href = href
		self.country = country
		self.id = id
		self.author = author
		self.date = date
		self.data = {}


#Completed Map
class CompletedMap(AutoRepr):
	def __init__(self,t1:Team , t2:Team   , m_map:str , score:str ,date:str="", mevent:Event=None):
		self.t1 = t1
		self.t2 = t2
		self.date = date
		self.score = score
		self.map = m_map
		self.set_status()

	def set_status(self):
		if(self.score.split("-")[0] > self.score.split("-")[1]):
			self.winner = self.t1
			self.loser = self.t2
		else:
			self.winner = self.t2
			self.loser = self.t1

