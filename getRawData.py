#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:36:35 2020

@author: carla
"""

#must start at 42 March 2nd


from parsePDF import * 
from createDB import * 
import pandas as pd


def main():
    db = '/home/carla/PythonProjects/COVID19_Monitoring/COVID19'
    conn = sqdb.connect(db)
    cursor = conn.cursor()
    cs = cursor.execute('SELECT max(id) FROM files_url')
    max_id = cs.fetchone()[0]
    t1 = 'WesternPacific'
    t2 = 'European'
    t3 = 'SouthEastAsia'
    t4 = 'EasternMediterranean'
    t5 = 'Americas'
    t6 = 'Africa'

    for counter in range(102, max_id+1): #42
        query = cursor.execute('SELECT PDF_link from files_url where id = (?)', (counter,)).fetchall()
        parser = ParsePDF(query[0][0]
                      , '/home/carla/PythonProjects/COVID19_Monitoring/temp')
        parser.downloadPDF()
        westernPacificDB, EuropeanDB, SouthEastAsiaDB, EasternMediterraneanDB, AmericasDB, AfricaDB = parser.extractTable()
        parser.deletePDF()
        createDB(db, westernPacificDB, t1, 'append')
        createDB(db, EuropeanDB, t2, 'append')
        createDB(db, SouthEastAsiaDB, t3, 'append')
        createDB(db, EasternMediterraneanDB, t4, 'append')
        createDB(db, AmericasDB, t5, 'append')
        createDB(db, AfricaDB, t6, 'append')
        
    conn.close()

if __name__== "__main__":
    main()
