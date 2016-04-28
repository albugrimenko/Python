# -*- coding: utf-8 -*-

#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")
from time import time

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from feature_format import featureFormat, targetFeatureSplit
from tester import test_classifier
#from FeatureSelection_PCA import pca_testdataset

import DataExploration as de
import Classifiers as cl

# Set to True for auto selected features (using SelectKBest algorithm)
_IS_KBEST_FEATURES_ = False
# Set to True to include extra features
_IS_INCLUDE_ADDITIONAL_FEATURE_ = True
# Set to True for DEFAULT algorithms parameters
_IS_DEFAULT_PARAMS_ = False
# Set to True for the best parameters search mode. 
# NOTE: can take a long time to run when True!
_IS_PARAMS_SEARCH_ = False

_IS_NB_ = True
_IS_DT_ = True
_IS_AB_ = True
_IS_RF_ = True

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = []
if _IS_KBEST_FEATURES_ == True:
    features_list = ["poi",
                    "salary", 
                    "from_messages", 
                    "shared_receipt_with_poi", 
                    "deferred_income",
                    "to_messages",
                    "bonus"
                    ]
    #reversed feature list
    #features_list = ["poi",
    #                "long_term_incentive", 
    #                "other", 
    #                "loan_advances", 
    #                "exercised_stock_options",
    #                "restricted_stock",
    #                "restricted_stock_deferred",
    #                "expenses",
    #                "total_payments"
    #                ]
else:
    features_list = ["poi",
                    #"salary", 
                    "bonus", 
                    "total_payments", 
                    #"loan_advances",
                    #"total_stock_value",
                    "exercised_stock_options"
                    #"shared_receipt_with_poi",
                    #"restricted_stock",
                    #"long_term_incentive"
                    ]
    if _IS_INCLUDE_ADDITIONAL_FEATURE_ == True:
        features_list.append('total_compensation')

### Load the dictionary containing the dataset
with open("../final_project/final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
de.dataset_outlier_cleaner(data_dict)

### Task 3: Create new feature(s)
my_dataset = data_dict
# add additional features (manually constructed)
if _IS_INCLUDE_ADDITIONAL_FEATURE_ == True:
    de.features_add(my_dataset)

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

# rescale features to be in [0..1] range
#scaler = MinMaxScaler()
#features = scaler.fit_transform(features)

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

# --- NaiveBayes ---
if _IS_NB_ == True:
    if _IS_PARAMS_SEARCH_ == True:
        print '=== NaiveBayes: no parameters to research ==='
    else:
        fclf = cl.NaiveBayes(features_train, labels_train, \
                            #features_test, labels_test, \
                            True, _IS_DEFAULT_PARAMS_)
        clf = Pipeline([('scaler', MinMaxScaler()), ('NB', fclf)])
        test_classifier(clf, my_dataset, features_list, folds=1000)
    print '-------------------------'

# --- SVM ---
#clf = cl.SVC(features_train, labels_train, True)
#test_classifier(clf, my_dataset, features_list, folds=1000)
#print '-------------------------'

# --- DecisionTree ---
if _IS_DT_ == True:
    if _IS_PARAMS_SEARCH_ == True:
        # -- search for the best parameters
        t0 = time()
        cl.GridSearch_DT(features, labels)
        print "-- search time:", round((time()-t0), 3), "s"
        '''
        === The best score: 0.8681  --- classifier is === 
        DecisionTreeClassifier(class_weight=None, criterion='gini', 
            max_depth=4,  max_features=None, max_leaf_nodes=None, 
            min_samples_leaf=1,  min_samples_split=2, 
            min_weight_fraction_leaf=0.0, random_state=42, splitter='best')
        -- search time: 0.11
        '''
    else:
        fclf = cl.DecisionTree(features_train, labels_train, True, 
                              _IS_DEFAULT_PARAMS_)
        clf = Pipeline([('scaler', MinMaxScaler()), ('DT', fclf)])
        test_classifier(clf, my_dataset, features_list, folds=1000)
    print '-------------------------'

# --- AdaBoost ---
if _IS_AB_ == True:
    if _IS_PARAMS_SEARCH_ == True:
        # -- search for the best parameters
        t0 = time()
        cl.GridSearch_AdaBoost(features, labels)
        print "-- search time:", round((time()-t0), 3), "s"
        '''
        === The best score: 0.8403  --- classifier is: ===
        AdaBoostClassifier(algorithm='SAMME',
          base_estimator=DecisionTreeClassifier(class_weight=None, 
            criterion='gini', max_depth=7,
            max_features=None, max_leaf_nodes=None, min_samples_leaf=1,
            min_samples_split=2, min_weight_fraction_leaf=0.0,
            random_state=42, splitter='best'),
          learning_rate=0.25, n_estimators=5, random_state=42)
          -- search time: 2.435 
        '''
    else:
        fclf = cl.AdaBoost(features_train, labels_train, True, 
                          _IS_DEFAULT_PARAMS_)
        clf = Pipeline([('scaler', MinMaxScaler()), ('AdaBoost', fclf)])
        test_classifier(clf, my_dataset, features_list, folds=1000)
    print '-------------------------'

# --- RandomForest ---
if _IS_RF_ == True:
    if _IS_PARAMS_SEARCH_ == True:
        # -- search for the best parameters
        t0 = time()
        cl.GridSearch_RandomForest(features, labels)
        print "-- search time:", round((time()-t0)/60., 3), "m"
        '''
        === The best score: 0.8958  --- classifier is: ===
        RandomForestClassifier(bootstrap=True, class_weight=None, 
            criterion='entropy',
            max_depth=4, max_features=None, max_leaf_nodes=None,
            min_samples_leaf=1, min_samples_split=3,
            min_weight_fraction_leaf=0.0, n_estimators=5, n_jobs=1,
            oob_score=False, random_state=42, verbose=0, warm_start=False)
        -- search time: 2.601 
        '''
    else:
        fclf = cl.RandomForest(features_train, labels_train, True, 
                              _IS_DEFAULT_PARAMS_)
        clf = Pipeline([('scaler', MinMaxScaler()), ('RF', fclf)])
        test_classifier(clf, my_dataset, features_list, folds=1000)
    print '-------------------------'
