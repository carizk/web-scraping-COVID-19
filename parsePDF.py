#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:35:49 2020

@author: carla
"""
        
 ##url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'
## header =  {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
##path = '/home/carla/PythonProjects/COVID19_Monitoring/'

from tabulate import tabulate
import requests 
import sqlite3 as sqdb
import os
import pandas as pd
import PyPDF4 as pdf
import numpy as np
from datetime import datetime
from itertools import groupby, chain
import string
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from createDB import *
import io

class ParsePDF:
    
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.titles = None
  #      self.totals = None
        self.WesternPacific = None 
        self.European = None 
        self.SouthEastAsia = None 
        self.EasterMediterranean = None 
        self.Americas = None 
        self.Africa = None 
        self.content = None
        self.date = None
        self.index = None

    def downloadPDF(self):
        file = requests.get(self.url)
        open(self.path, 'wb').write(file.content)
        
    
    def deletePDF(self):
        os.remove(self.path)
    
            
    def concatenateStrings(self, list_name):
        isString = lambda x: isinstance(x, str)
        new_list = list(chain.from_iterable(
                    (' '.join(group), ) if group_isstr else group
                    for group_isstr, group in groupby(list_name, isString)
                    ))           
        return new_list

    def extract_text_from_pdf(self,pdf_path):
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
                page_interpreter.process_page(page)
            
        text = fake_file_handle.getvalue()
    
    # close open handles
        converter.close()
        fake_file_handle.close()
    
        if text:
            return text

    
    
    def extractTable(self):
        file = open(self.path, 'rb')
     #   read_pdf = pdf.PdfFileReader(file)
        read_pdf = self.extract_text_from_pdf(self.path)
        
        # parse pages
        self.content = read_pdf
        
        # split into list by '\n'  
        self.content = self.content.split()
   
        
        #export file to txt to better visualize
        with open('textPrint.txt', 'w') as f:
           f.write(str(self.content))        
    
        #create list of regions to help in parsing


        regions = ['Western', 'European',  'South-East', 'Eastern', 'Americas' , 'African']
      
        #column headers
        columns = ['reporting_country', 'total_confirmed_cases', 'total_confirmed_new_cases','total_deaths' ,'total_new_deaths', 'days_since_last_reported_case']
        sub = []
        all_lists = [[]]
        
          
  #write file to text to better analyze      
#        with open('textPrint.txt', 'w') as f:
#            f.write(str(self.content))   
        content = self.content
        self.content = self.content[self.content.index('SURVEILLANCE'):]
        
        # convert digits to int type
        for index, obj in enumerate(self.content):
            result = True
            try: 
                int(''.join(c for c in obj if c.isdigit()))
                result = True
            except ValueError:
                result = False
            if result:
                self.content[index] = int(''.join(c for c in obj if c.isdigit()))

        #divide into sub-tables by region
        for index, obj in enumerate(regions):
            start = self.content.index(obj)
            end = 0
            if index < (len(regions)-1):
                end = self.content.index(regions[index+1])
                sub = self.content[start:end]
               
            else: # for last table
                sub = self.content[start:]
                ind = 0
                
                #remove text not in table
                if '*Case' in sub:
                    ind = sub.index('*Case')
                elif '*Numbers' in sub:
                    ind = sub.index('*Numbers') 
                    sub = sub[:ind]
            all_lists.append(sub)
    
        
        # remove unnecessary records
        for index, l in enumerate(all_lists):
            if index == 4:
                all_lists[4] = l[:len(l)-3]
                
        all_lists = list(filter(None, all_lists)) # remove empty lists
        
        # get title of tables
        titles = []

        
        for index, l in enumerate(all_lists):
            if index != 4:
                end = l.index('Region')
                titles.append(l[:end+1])
                all_lists[index] = l[end+1:] # remove title from list\
            else:
                end = l.index('Americas')
                titles.append(l[:end+1])
                all_lists[index] = l[end+1:] # remove title from list
            #remove subtotals and separate totals
            new = []
            if index == 5:
                start_sub = all_lists[5].index('Subtotal')
                end_sub = all_lists[5].index('International')
                new = all_lists[5][end_sub:] # new list of totals
                all_lists[index] = all_lists[5][:start_sub ] # remove

        # remove word territories from all lists
        
        for index, obj in enumerate(all_lists):
            if index != 2:
                if 'Territories**' in obj:
                    all_lists[index].remove('Territories**')

        # concatenate strings
        for index, obj in enumerate(all_lists):
            all_lists[index] = self.concatenateStrings(obj)
        
        # concatenate titles
        for index, t in enumerate(titles):
            titles[index] = self.concatenateStrings(t)

        titles = list(chain.from_iterable(titles))
        titles[4] = 'Region of the Americas'
        
        classification = ['sporadic cases' ,'cluster of cases','clusters of cases', 'pending', 'community transmission', 'local transmission', 'imported cases only', 'under investigation']
        
        for index, obj in enumerate(all_lists):
            all_lists[index] = [x for x in obj if not any(c in str(x).lower() for c in classification)]
            

        # transform lists to dataframe and append date and ID
        self.content = content


        # split lists into dataframes for each region

        #western pacific 
        westPacifictemp = np.array_split(all_lists[0], len(all_lists[0])/6)
        self.WesternPacific = pd.DataFrame(westPacifictemp, columns = columns)
        self.WesternPacific['Report_ID'] = self.extractIndex()
        self.WesternPacific.insert(0, 'Date', self.extractDate())
        self.WesternPacific.set_index('Report_ID', inplace=True)
                
        # European region
        
        europeanTemp = np.array_split(all_lists[1], len(all_lists[1])/6)
        self.European = pd.DataFrame(europeanTemp, columns = columns)
        self.European['Report_ID'] = self.extractIndex()
        self.European.insert(0, 'Date', self.extractDate())
        self.European.set_index('Report_ID', inplace = True )
                
        # South-East Asia
        tmp = np.array_split(all_lists[2], len(all_lists[2])/6)
        self.SouthEastAsia = pd.DataFrame(tmp, columns = columns)
        self.SouthEastAsia['Report_ID'] = self.extractIndex()
        self.SouthEastAsia.insert(0, 'Date', self.extractDate())
        self.SouthEastAsia.set_index('Report_ID', inplace = True )
        
        # Eastern Mediterranean 
        tmp = np.array_split(all_lists[3], len(all_lists[3])/6)
        self.EasterMediterranean  = pd.DataFrame(tmp, columns = columns)
        self.EasterMediterranean['Report_ID'] = self.extractIndex()
        self.EasterMediterranean.insert(0, 'Date', self.extractDate())
        self.EasterMediterranean.set_index('Report_ID', inplace = True )
        
        
        #Americas

        tmp = np.array_split(all_lists[4], len(all_lists[4])/6)
        self.Americas  = pd.DataFrame(tmp, columns = columns)
        self.Americas['Report_ID'] = self.extractIndex()
        self.Americas.insert(0, 'Date', self.extractDate())
        self.Americas.set_index('Report_ID', inplace = True )
        
        
        #African
        tmp = np.array_split(all_lists[5], len(all_lists[5])/6)
        self.Africa  = pd.DataFrame(tmp, columns = columns)
        self.Africa['Report_ID'] = self.extractIndex()
        self.Africa.insert(0, 'Date', self.extractDate())
        self.Africa.set_index('Report_ID', inplace = True )
        
        return self.WesternPacific, self.European, self.SouthEastAsia, self.EasterMediterranean, self.Americas, self.Africa
        
    def extractIndex(self):
        index = 0
        id = self.content.index('Report')
        self.index = self.content[id+1:id+3]
        self.index = ''.join(self.index[1])
        return self.index
    
    def extractDate(self):
        index = 0
        for i, elem in enumerate(self.content):
            if 'CET' in str(elem):
                index = i
            elif 'CEST' in str(elem):
                index = i
            if index!= 0:
                break
        start = index
        end = self.content.index('Coronavirus')
        self.date = self.content[start+1:end]
        self.date = datetime.strptime( " ".join(self.date), '%d %B %Y').date()
        return self.date
    

