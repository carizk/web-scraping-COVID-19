#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 15:24:43 2020

@author: carla
"""


        
 ##url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
## header =  {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
##path = '/home/carla/PythonProjects/COVID19_Monitoring/'
 
from scrape import *
import pandas as pd
from createDB import *
from tabulate import tabulate

def main():
    
    links = [] # for pdf links
    count = [] # for pdf count 
    
    db = '/home/carla/PythonProjects/COVID19_Monitoring/COVID19'#new db name
    table = 'files_url' #new table name
    url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
    header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    
    # create object
    content = Scrape(url, header)
    
    #get content
    links, count = content.getLinks()
    #create df to input content
    df = pd.DataFrame(list(zip(count, links)), columns = ['ID', 'PDF_link'])
    df = df.sort_values(by = ['ID'])
    df.set_index('ID', inplace=True)
    
    #create db and insert values
    createDB(db, df, table, 'replace')
    
#run program

if __name__== "__main__":
    main()

    