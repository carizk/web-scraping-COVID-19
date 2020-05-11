#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:45:31 2020

@author: carla
"""

import sqlite3 as sqdb
from sqlite3 import Error
import pandas as pd

def createDB(db, df, table, action):
     conn = None
     try:
         conn = sqdb.connect(db)
         print(sqdb.version)
     except Error as e:
         print(e)
     finally:
         if conn:
             df.to_sql(table, conn, if_exists = action)
             conn.close()