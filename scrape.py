#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 08:38:13 2020

@author: carla
"""
## Class to scrape WHO website 

from bs4 import BeautifulSoup
import urllib.request as ur
from urllib.error import HTTPError
from urllib.error import URLError
from collections import OrderedDict



class Scrape: 
    
    def __init__(self, url, header, counter = 0):
        self.url = url 
        self.header = header
        self.counter = counter
        self.count = []
        self.links = []
    
    def getLinks(self):
        req = ur.Request(url = self.url, headers = self.header)
        try:
            html = ur.urlopen(self.url)
        except HTTPError as e:
            print(e)
        except URLError as e:
            print("The server could not be found")
        else:
            html = html.read()
            soup = BeautifulSoup(html, "html.parser")
            href = []
        
            # get all links that are in pdf format
            href = soup.find_all("a", href=lambda href: "/docs" in href)
            for h in href:
                self.links.append('https://who.int' + h.get('href'))
        
            self.links = list(OrderedDict.fromkeys(self.links)) 
            for h in href: 
                self.count.append([int(i) for i in str(h.text).split() if i.isdigit()])     
            
            self.count = [ item for elem in self.count for item in elem]
            self.count = list(dict.fromkeys(self.count))
            self.links = list(dict.fromkeys(self.links))
            return self.links, self.count
                
                
    def update(self):
        req = ur.Request(url = self.url, headers = self.header)
        try:
            html = ur.urlopen(self.url)
        except HTTPError as e:
            print(e)
        except URLError as e:
            print("The server could not be found")
        else:
            html = html.read()
            soup = BeautifulSoup(html, "html.parser")
            href = soup.find("a", href=lambda href: "/docs" in href)
            newLink = 'https://who.int' + href.get('href')
            self.count = int(''.join(filter(str.isdigit, href.text)))

            if self.counter == self.count:
                return
            elif self.counter < self.count:
                return newLink, self.count
            
            return newLink, self.count
    

    
        
        
        
 ##url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
## header =  {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
##path = '/home/carla/PythonProjects/COVID19_Monitoring/'

 
 
 