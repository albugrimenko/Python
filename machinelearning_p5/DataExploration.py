# -*- coding: utf-8 -*-

""" 
    Starter code for exploring the Enron dataset (emails + finances);
    loads up the dataset (pickled dict of dicts).

    The dataset has the form:
    enron_data["LASTNAME FIRSTNAME MIDDLEINITIAL"] = { features_dict }

    {features_dict} is a dictionary of features associated with that person.
    You should explore features_dict as part of the mini-project,
    but here's an example to get you started:

    enron_data["SKILLING JEFFREY K"]["bonus"] = 5600000
"""

''' 
A python dictionary can’t be read directly into an sklearn classification or regression algorithm; 
instead, it needs a numpy array or a list of lists (each element of the list (itself a list) is a 
data point, and the elements of the smaller list are the features of that point).

We’ve written some helper functions (featureFormat() and targetFeatureSplit() in 
tools/feature_format.py) that can take a list of feature names and the data dictionary, and 
return a numpy array.

In the case when a feature does not have a value for a particular person, this function will 
also replace the feature value with 0 (zero).
'''
import pickle
import sys
import math
import matplotlib.pyplot
sys.path.append("../tools/")
from feature_format import featureFormat

def isFloat(v):
    try:
        float(v)
        return True
    except ValueError:
        return False
        
def getFloatOrZero(v):
    try:
        f = float(v)
        if  math.isnan(f):
            return 0
        else:
            return f
    except ValueError:
        return 0

def dataset_describe(isPrintChiefs = False):
    enron_data = pickle.load(open("../final_project/final_project_dataset.pkl", "r"))

    print '----- Enron Finances -----'
    print '-- # elements:', len(enron_data)
    print '-- structure: --'
    s = set()
    for k in enron_data.keys():
        for a in enron_data[k]:
            s.add(a)

    print s
    print '-- # attributes:', len(s)

    poi = [x for x in enron_data.keys() if enron_data[x]['poi'] == True]
    print '-- # Persons of Interest (POI):', len(poi)
    print '-- Persons of Interest (POI):'
    print poi

    if isPrintChiefs:
        print '-- CEO, Chairman, CFO --'
        # LAY KENNETH L, SKILLING JEFFREY K, FASTOW ANDREW S
        #“total_payments” feature - took home the money
        chiefs = [x for x in enron_data.items() 
            if x[0] == 'LAY KENNETH L' or x[0] == 'SKILLING JEFFREY K' or x[0] == 'FASTOW ANDREW S']
        chiefs = sorted(chiefs, key=lambda s: s[1]['total_payments'])
        print chiefs
    
    # how many people have salary?
    print '-- # people with salary populated:', len([x for x in enron_data.values() if math.isnan(float(x['salary'])) == False])
    # how many people have email?
    print '-- # people with email populated:', len([x for x in enron_data.values() if x['email_address'] != '' and x['email_address'] != 'NaN'])

    # what % of people have NaN as their total payments?
    tot = len(enron_data)
    noPayments = len([x for x in enron_data.values() if math.isnan(float(x['total_payments'])) == True])
    print '-- % of people have NaN as their total payments:', "{0:.2f}%".format(float(noPayments)*100/float(tot))
    # the same for POI
    tot = len([x for x in enron_data.values() if x['poi']])
    noPayments = len([x for x in enron_data.values() if x['poi'] == True and math.isnan(float(x['total_payments'])) == True])
    print '-- % of POI have NaN as their total payments:', "{0:.2f}%".format(float(noPayments)*100/float(tot))
    noData = len([x for x in enron_data.values() if 
        math.isnan(float(x['total_payments'])) == True and 
        math.isnan(float(x['salary'])) == True and 
        math.isnan(float(x['bonus'])) == True and 
        math.isnan(float(x['total_stock_value'])) == True])
    print '-- % of people have no data:', "{0:.2f}%".format(float(noData)*100/float(tot))

    print "=== Outliers (by salary) ==="
    for k in enron_data.keys():
        if (float(enron_data[k]["salary"]) > 10000000):  #2.5e7
            print k, enron_data[k]

    #print "=== Features Stats ==="
    dataset_outlier_cleaner(enron_data)
    ind = range(len(s))
    names = []
    for name in s:
        names.append(name)
    data = []
    for v in enron_data.values():
        data.append(v)
    features_describe(data, ind, names)
    return

def dataset_outlier_cleaner(data):
    data.pop("TOTAL", 0)
    
def dataset_explore():
    enron_data = pickle.load( open("../final_project/final_project_dataset.pkl", "r") )
    features = ["salary", "bonus"]

    # === Complete dataset ===
    data = featureFormat(enron_data, features)
    features_plot(data, 0, 1, 'salary', 'bonus', 'Complete dataset')
    
    # === Dataset without outliers ===
    dataset_outlier_cleaner(enron_data)
    data = featureFormat(enron_data, features)
    features_plot(data, 0, 1, 'salary', 'bonus', 'Dataset without outliers')

    return

def features_plot(data, indX, indY, labelX='', labelY='', title=''):
    for point in data:
        matplotlib.pyplot.scatter( point[indX], point[indY] )
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel(labelX)
    matplotlib.pyplot.ylabel(labelY)
    matplotlib.pyplot.show()
    return

def features_describe(data, indices, names, isPrint = True):
    ''' Gets basic stats on each column (feature) in data.
    
        data is a list of sets.
        Indices defines what columns to be analyzed - properties names.
        Names is a list of features names.
    '''
    stat = {}
    for j in indices:
        stat[names[j]] = {
            "min": float('nan'),
            "max": float('nan'),
            "sum": 0.,
            "cnt": 0,
            "cnt_na": 0,
            "cnt_zero": 0
        }
    #print 'Dimensions:', len(data), 'x', len(indices)
    
    for i in range(len(data)):
        for j in indices:
            stat[names[j]]["cnt"] += 1
            if isFloat(data[i][names[j]]):
                st = stat[names[j]]
                x = float(data[i][names[j]])
                if math.isnan(x):
                    st["cnt_na"] += 1
                else:
                    if x == 0:
                        st["cnt_zero"] += 1
                    if (math.isnan(st["min"]) or st["min"] > x):
                        st["min"] = x
                    if (math.isnan(st["max"]) or st["max"] < x):
                        st["max"] = x
                    st["sum"] += x
            else:
                stat[names[j]]["cnt_na"] += 1
    #stat = sorted(stat, key=lambda k: k[0])
    if isPrint:
        print '=== Features: ==='
        for j in indices:
            print names[j], '\r\n-------------'
            st = stat[names[j]]
            print 'min:', "{:,.2f}".format(st["min"])
            if st["cnt"] != 0:
                print 'mean:', "{0:,.2f}".format(st["sum"] / st["cnt"])
            else:
                print 'mean: na'
            print 'max:', "{0:,.2f}".format(st["max"])
            print 'count:', st["cnt"]
            if st["cnt"] > 0:
                print 'na:', st["cnt_na"], " ({0:.2f}%)".format(st["cnt_na"]*100/st["cnt"])
                print 'zeros:', st["cnt_zero"], " ({0:.2f}%)".format(st["cnt_zero"]*100/st["cnt"])
            print '\r\n'
    return stat

def features_add(my_dataset):
    ''' Adds total & diferred compensation to dataset '''
    for k in my_dataset.keys():
        my_dataset[k]["total_compensation"] = \
            getFloatOrZero(my_dataset[k]["bonus"]) + \
            getFloatOrZero(my_dataset[k]["director_fees"]) + \
            getFloatOrZero(my_dataset[k]["exercised_stock_options"]) + \
            getFloatOrZero(my_dataset[k]["expenses"]) + \
            getFloatOrZero(my_dataset[k]["loan_advances"]) + \
            getFloatOrZero(my_dataset[k]["long_term_incentive"]) + \
            getFloatOrZero(my_dataset[k]["other"]) + \
            getFloatOrZero(my_dataset[k]["restricted_stock"]) + \
            getFloatOrZero(my_dataset[k]["salary"]) + \
            getFloatOrZero(my_dataset[k]["total_payments"]) + \
            getFloatOrZero(my_dataset[k]["total_stock_value"]) + \
            getFloatOrZero(my_dataset[k]["deferral_payments"]) + \
            getFloatOrZero(my_dataset[k]["restricted_stock_deferred"])
    
        my_dataset[k]["diferred_compensation"] = \
            getFloatOrZero(my_dataset[k]["deferral_payments"]) + \
            getFloatOrZero(my_dataset[k]["deferred_income"]) + \
            getFloatOrZero(my_dataset[k]["restricted_stock_deferred"])
    return
# ------------------ MAIN -------------
if __name__ == '__main__':
    dataset_describe()
    #dataset_explore()