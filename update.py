#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 22:18:11 2020

@author: carla
"""

from scrape import *
import pandas as pd
from createDB import *
import schedule 
import time

def main():
    links = []
    count = []

    db = '/home/carla/PythonProjects/COVID19_Monitoring/COVID19'#db name
    table = 'files_url' #table name
    
    conn = None
    try:
        conn = sqdb.connect(db)
        print(sqdb.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            cursor = conn.cursor()
            cursor = cursor.execute('SELECT max(id) FROM files_url')
            max_id = cursor.fetchone()[0]
            conn.close()
    url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
    header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    content = Scrape(url, header, max_id)
    links, count = content.update()
    temp = []
    temp.append(count)
    temp.append(links)

    df = pd.DataFrame(temp)
    df = df.transpose()
    df.columns = ['ID', 'PDF_link']
    df.set_index('ID', inplace=True)
     
#    print(df)
    
    #create db and insert values
    createDB(db, df, table, 'append')

#schedule.every().day.at("19:00").do(jobUpdate)

#while True:
#    schedule.run_pending()
#    time.sleep(1)

if __name__ == "__main__":
    main()