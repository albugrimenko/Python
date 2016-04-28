# -*- coding: utf-8 -*-

import sys
from time import time
sys.path.append("../tools/")

#from sklearn.metrics import precision_recall_fscore_support
#from sklearn.metrics import precision_score
#from sklearn.metrics import recall_score
#from sklearn.metrics import f1_score

def NaiveBayes(features_train, labels_train, #features_test, labels_test, 
               isPrint=True, isDefaultParams = False):
    ''' Naive Bayes classifier '''
    from sklearn.naive_bayes import GaussianNB
    t0 = time()
    clf = GaussianNB()
    clf = clf.fit(features_train, labels_train)
    if isPrint:
        #tt = time()
        #predictions = clf.predict(features_test)
        #tp = time()
        print '=== GaussianNB ==='
        print "-- training time:", round(time()-t0, 3), "s"
        #print "-- prediction time:", round(tp-tt, 3), "s"
        #print "-- Accuracy:", clf.score(features_test, labels_test)
        #print "-- Precision:", precision_score(labels_test, predictions)
        #print "-- Recall:", recall_score(labels_test, predictions)
        #print "-- F1 Score:", f1_score(labels_test, predictions)
    return clf

def SVC(features_train, labels_train, #features_test, labels_test, 
             isPrint=True, isDefaultParams = False):
    ''' Support Vector Classification
    C: Penalty parameter C of the error term (default=1.0)
    kernel:  ‘linear’, ‘poly’, ‘rbf’, ‘sigmoid’, ‘precomputed’ or a callable
        default=’rbf’
    degree: the polynomial kernel function (‘poly’)
    gamma: Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’. 
        If gamma is ‘auto’ then 1/n_features will be used instead.
    probability : boolean (default=False) - whether to enable probability 
        estimates. This and will slow down method fit.
    max_iter: Hard limit on iterations within solver, or -1 for no limit.
        default=-1
    random_state: the seed used by the random number generator (default=None)
    '''
    from sklearn import svm
    t0 = time()
    clf = svm.SVC(random_state=42)
    if isDefaultParams == False:
        clf = svm.SVC(
            kernel='rbf', 
            C=10,
            probability=False,
            random_state=42
            ) 
    clf.fit(features_train, labels_train)
    if isPrint:
        print '=== SVM ==='
        print "-- training time:", round(time()-t0, 3), "s"
    return clf

def DecisionTree(features_train, labels_train, #features_test, labels_test, 
             isPrint=True, isDefaultParams = False):
    ''' Decision Tree:
    criterion: 'gini', 'entropy' for the information gain. (default=”gini”)
    splitter : 'best', 'random' (default=”best”)
    max_features: # features to consider when looking for the best split
        int/float value or 'auto', 'sqrt', 'log2', None (max_features=n_features)
        default is None
    max_depth: maximum depth of the tree (ignored if max_leaf_nodes is'nt None)
    min_samples_split: min # samples required to split an internal node
    min_samples_leaf: min # samples required to be at a leaf node
    max_leaf_nodes: Grow a tree with max_leaf_nodes in best-first fashion
        default=None
    class_weight: 
    random_state: the seed used by the random number generator (default=None)
    presort : bool (default=False)
        When using either a smaller dataset or a restricted depth, this may 
        speed up the training.
        
    NOTE: no data normalization required, BUT missing values should not exist
    '''
    from sklearn.tree import DecisionTreeClassifier
    t0 = time()
    clf = DecisionTreeClassifier(random_state=42)
    if isDefaultParams == False:
        clf = DecisionTreeClassifier(
            criterion='gini',       #gini
            max_features=None,      #None
            max_depth=7,            #None
            min_samples_leaf=1,     #1
            min_samples_split=2,    #2
            max_leaf_nodes=None,
            splitter='best',
            random_state=42
            )
    clf = clf.fit(features_train, labels_train)
    if isPrint:
        print '=== DecisionTree ==='
        print "-- training time:", round(time()-t0, 3), "s"
        print "-- Feature importances:\r\n", clf.feature_importances_
    return clf

def AdaBoost(features_train, labels_train, #features_test, labels_test, 
             isPrint=True, isDefaultParams = False):
    ''' AdaBoost Classifier
    An AdaBoost classifier is a meta-estimator that begins by fitting a 
    classifier on the original dataset and then fits additional copies of the 
    classifier on the same dataset but where the weights of incorrectly 
    classified instances are adjusted such that subsequent classifiers focus 
    more on difficult cases.

    n_estimators - max # of estimators (default 50)
    learning_rate - shrinks the contribution of each classifier by 
                    learning_rate (default 1)
        There is a trade-off between learning_rate and n_estimators.
    algorithm : {‘SAMME’, ‘SAMME.R’}, optional (default=’SAMME.R’)
        SAMME - the SAMME discrete boosting algorithm
        SAMME.R - real boosting algorithm
    '''
    #from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import AdaBoostClassifier
    t0 = time()
    # Decision Tree with default parameters
    #dt = DecisionTreeClassifier(random_state=42)
    #dt.fit(features_train, labels_train)
    dt = DecisionTree(features_train, labels_train, False, isDefaultParams)
    tdt = time()
    clf = AdaBoostClassifier(base_estimator=dt, random_state=42)
    if isDefaultParams == False:
        clf = AdaBoostClassifier(
            base_estimator=dt,
            n_estimators=5,     #50
            learning_rate=0.50, #1
            algorithm="SAMME",  #SAMME.R
            random_state=42
            )
    clf.fit(features_train, labels_train)
    if isPrint:
        t1 = time()
        print '=== AdaBoost ==='
        print "-- training time:", round(time()-tdt, 3), "s"
        print "-- total training time (incl DT):", round(t1-t0, 3), "s"
        print "-- Feature importances:\r\n", clf.feature_importances_
    return clf
    
def RandomForest(features_train, labels_train, #features_test, labels_test, 
             isPrint=True, isDefaultParams = False):
    ''' The main parameters to adjust when using these methods is 
    n_estimators - # trees in the forest (default 10)
    max_features - size of the random subsets of features to consider when 
        splitting a node (values: auto, sqrt, log2, None). The lower the 
        greater the reduction of variance, but also the greater the increase 
        in bias.
    Note that results will stop getting significantly better 
    beyond a critical number of trees.
    
    Empirical good default values are max_features=n_features for 
    regression problems, and max_features=sqrt(n_features) for classification 
    tasks (where n_features is the number of features in the data). Good 
    results are often achieved when setting max_depth=None in combination with
    min_samples_split=1 (i.e., when fully developing the trees). 
    Bear in mind though that these values are usually not optimal, and might 
    result in models that consume a lot of ram. The best parameter values 
    should always be cross-validated. In addition, note that in random forests,
    bootstrap samples are used by default (bootstrap=True) while the default 
    strategy for extra-trees is to use the whole dataset (bootstrap=False). 
    When using bootstrap sampling the generalization error can be estimated 
    on the left out or out-of-bag samples. This can be enabled by setting
    oob_score=True.
    '''
    from sklearn.ensemble import RandomForestClassifier
    t0 = time()
    clf = RandomForestClassifier(random_state=42)
    if isDefaultParams == False:
        clf = RandomForestClassifier(
            criterion='gini',
            n_estimators=25,        # trees in the forest (default 10)
            max_depth=9,            # The maximum depth of the tree.
            min_samples_split=2,    # 1 - fully developing the trees
            min_samples_leaf=1,
            max_features=None,    # sqrt, log2, None
            bootstrap=True,         # False for the whole dataset, True for samples
            max_leaf_nodes=None,
            random_state=42          # the seed used by the random number generator
            )
    clf.fit(features_train, labels_train)
    if isPrint:
        print '=== RandomForest ==='
        print "-- training time:", round(time()-t0, 3), "s"
        print "-- Feature importances:\r\n", clf.feature_importances_
    return clf

def GridSearch(clf, params, features_train, labels_train):
    from sklearn import grid_search
    grid = grid_search.GridSearchCV(clf, params)
    grid.fit(features_train, labels_train)
    print '=== The best score:', "{0:.4f}".format(grid.best_score_) ,' --- classifier is: ===\r\n', grid.best_estimator_
    return

def GridSearch_DT(features_train, labels_train):    
    from sklearn.tree import DecisionTreeClassifier
    params = {
        'criterion':('gini', 'entropy'),            # gini
        'max_depth':[None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],   # None
        #'min_samples_split':[1, 2, 3, 4, 5, 7, 10], # 2
        #'min_samples_leaf':[1, 2, 3, 4, 5, 7, 10]  # 1
        #'max_features': [None, 4, 'sqrt', 'log2']   # None
        }
    clf = DecisionTreeClassifier(
        random_state=42
    )
    GridSearch(clf, params, features_train, labels_train)
    return

def GridSearch_AdaBoost(features_train, labels_train):    
    from sklearn.ensemble import AdaBoostClassifier
    dt = DecisionTree(features_train, labels_train, False, False)
    params = {
        'algorithm':('SAMME', 'SAMME.R'), 
        'n_estimators':[5, 10, 15, 20, 50, 100, 150, 200, 250, 300],
        'learning_rate':[0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2., 2.25, 2.5]
        }
    clf = AdaBoostClassifier(
        base_estimator=dt, random_state=42
    )
    GridSearch(clf, params, features_train, labels_train)
    return

def GridSearch_RandomForest(features_train, labels_train):    
    from sklearn.ensemble import RandomForestClassifier
    params = {
        'criterion':['gini', 'entropy'],
        'max_features':['auto', 'sqrt', 'log2', None], 
        'n_estimators':[5, 10, 15, 20, 50],  #, 100, 150, 200, 250, 300],
        'max_depth':[None, 1, 2, 3, 4, 5],
        'min_samples_split':[1, 2, 3, 4, 5],
        'bootstrap':[True, False]
        }
    clf = RandomForestClassifier(random_state=42)
    GridSearch(clf, params, features_train, labels_train)
    return


# ---------- MAIN ---------
if __name__ == '__main__':
    print '~~~ There is no main method defined. ~~~'