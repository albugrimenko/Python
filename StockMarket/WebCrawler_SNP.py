# -*- coding: utf-8 -*-
#
# Crawl the web, extract data and 
# store HTML files in a local folder (./Temp_Data)
# for future processing
#
# Get current S&P 500 list using
# exec [tools].[SNP_StockList]
#
#
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

DATADIR = './Data/'

def save_to_file(filename, data):
    with open(filename, 'w') as fout:
        if type(data) is list:
            fout.write("\n".join(data))
        else:
            fout.write(data)
    print '--- saved data to: ', filename
    return

def make_request_get(url, data):
    r = requests.get(url, data)
    print '--- got data from: ', url
    return r.text
    
def compare_lists(list_old, list_new):
    ''' Searches the difference between two lists and returns two sets:
    first - items that should be deleted from "old" list
    second - items that should be added to the "old" list'''
    tbd = set(list_old)     # at the end will be "to be deleted"
    tbi = set()             # to be inserted
    for item in list_new:
        if item in tbd:
            tbd.remove(item)
        else:
            tbi.add(item)
    return tbd, tbi
    

### ------------ custom (temp) ----------------
def getSNPStockListFromFile(filename, isSaveResult):
    ''' Gets stock list from html file and returns as a list 
    If isSaveResult is True, the resul list will be saved in the file'''
    ar = []
    fn = filename + '.res'
    with open(filename, "r") as html:
        soup = BeautifulSoup(html)
        t = soup.find("input", {"name" : "symbols"})
        if t is not None:
            ar = t['value'].split(',')
            ar = [a.strip() for a in ar if len(a.strip()) > 0]
            ar.sort()
            print '--- Got Stock List: ', len(ar), ' symbol(s) found'
            if isSaveResult:
                save_to_file(fn, ar)
    return ar, fn
    
### ------------ solutions -------------
    
def getSNPStockList(compareToFileName):
    ''' Date formats:
    %d is the day number
    %m is the month number
    %b is the month abbreviation
    %y is the year last two digits
    %Y is the all year '''
    today = datetime.today()
    filename = os.path.join(DATADIR, 'SNP_{:%m%d%Y}.htm'.format(today))
    html = make_request_get("http://www.barchart.com/stocks/sp500.php?_dtp1=0", None)
    save_to_file(filename, html)

    newList, newFileName = getSNPStockListFromFile(filename, True)
    if newList is not None and len(compareToFileName) > 0:
        with open(compareToFileName, "r") as f:
            oldList = f.read().splitlines()
        if oldList is not None:
            tbd, tbi = compare_lists(oldList, newList)
            print '--- Compared lists: ', len(tbd) + len(tbi), ' difference(s) found.'
            with open(newFileName + '.dif', 'w') as fout:
                fout.write("--- To Be Deleted ---\n")
                if tbd is not None and len(tbd) > 0:
                    fout.write("\n".join(sorted(tbd)))
                else:
                    fout.write("<NONE>\n")
                fout.write("\n\n--- To Be Inserted ---\n")
                if tbi is not None and len(tbi) > 0:
                    fout.write("\n".join(sorted(tbi)))
                else:
                    fout.write("<NONE>\n")
                print '--- Saved difference to: ', newFileName + '.dif'
    
### ---------- main calls -------------

getSNPStockList(os.path.join(DATADIR, 'SNP_InstrList_030116.csv'))

print ('=== DONE ===')
