# -*- coding: utf-8 -*-

#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from tester import test_classifier

import DataExploration as de
import Classifiers as cl

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ["poi",
                "bonus", 
                "total_payments", 
                "exercised_stock_options",

                # additional features
                "total_compensation"
                ]

### Load the dictionary containing the dataset
with open("../final_project/final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
de.dataset_outlier_cleaner(data_dict)

### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict
# add additional features (manually constructed)
de.features_add(my_dataset)

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

# rescale features to be in [0..1] range
scaler = MinMaxScaler()
features = scaler.fit_transform(features)

from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

print '--- Validating Results ---'
print "-- # features:", len(features_list)
print "-- # items in train:", len(labels_train)
print "-- # poi in train:", len([ x for x in labels_train if x==1])
print "-- # non-poi in train:", len([ x for x in labels_train if x==0])
print "--- Features List ---"
print features_list

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# --- THE BEST CLASSIFIER is RandomForest classifier with F1 Score = 0.414
# --- RandomForest ---
fclf = cl.RandomForest(features_train, labels_train)
clf = Pipeline([('scaler', MinMaxScaler()), ('RF', fclf)])
test_classifier(clf, my_dataset, features_list, folds=1000)
print '-------------------------'
    

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)

