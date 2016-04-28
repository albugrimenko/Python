# -*- coding: utf-8 -*-
from sklearn.decomposition import PCA

import pickle
import sys
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit


def pca_get(data, n_components=2):
    pca = PCA(n_components=n_components)
    pca.fit(data)
    return pca

def pca_plot_2components(data, data_transformed, first_pc, second_pc):
    import matplotlib.pyplot as plt
    for ii, jj in zip(data_transformed, data):
        plt.scatter( first_pc[0]*ii[0], first_pc[1]*ii[1], color="r")
        plt.scatter( second_pc[0]*ii[1], second_pc[1]*ii[1], color="c")
        plt.scatter( jj[0], jj[1], color="b")
    plt.show()
    return
    
def pca_test():
    ''' Principal Component Analysis testing '''
    enron_data = pickle.load(open("../final_project/final_project_dataset.pkl", "r"))
    features = [#"poi", 
                "salary", 
                "bonus", 
                "total_payments", 
                "loan_advances",
                "total_stock_value",
                "exercised_stock_options",
                "shared_receipt_with_poi",
                "restricted_stock"]
    data = featureFormat(enron_data, features)
    
    pca = pca_get(data, n_components=5)    
    print '--- explained_variance_ratio_ ---'
    print pca.explained_variance_ratio_  #prints variance for each component: .9 means 90%
    first_pc = pca.components_[0]
    second_pc = pca.components_[1]
    transformed_data = pca.transform(data)
    pca_plot_2components(data, transformed_data, first_pc, second_pc)

def pca_testdataset(dataset):
    ''' Principal Component Analysis on the defined dataset '''
    ds = dataset
    # remove 'poi'
    ds.pop("poi", None)
    pca = pca_get(ds, n_components=5)    
    print '--- explained_variance_ratio_ ---'
    print pca.explained_variance_ratio_  #prints variance for each component: .9 means 90%
    first_pc = pca.components_[0]
    second_pc = pca.components_[1]
    transformed_data = pca.transform(ds)
    pca_plot_2components(ds, transformed_data, first_pc, second_pc)
    return

def kbest_test():
    ''' Select K Best testing '''
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.feature_selection import SelectKBest
    from sklearn.feature_selection import chi2

    enron_data = pickle.load(open("../final_project/final_project_dataset.pkl", "r"))
    feature_list = ["poi", 
                "bonus",
                "deferral_payments",
                "deferred_income",
                "director_fees",
                "exercised_stock_options",
                "expenses",
                "from_messages",
                #"from_this_person_to_poi",
                #"from_poi_to_this_person",
                "loan_advances",
                "long_term_incentive",
                "other",
                "restricted_stock",
                "restricted_stock_deferred",
                "salary",
                "shared_receipt_with_poi",
                "to_messages",
                "total_payments",
                "total_stock_value"
                ]
    data = featureFormat(enron_data, feature_list)
    labels, features = targetFeatureSplit(data)
    
    # rescale features to be in [0..1] range
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)
    
    sk = SelectKBest(chi2, k=6) # f_classif
    data_new = sk.fit_transform(features_scaled, labels)
    #print data_new.shape
    
    feature_list_new = [x for x, y in 
        zip(feature_list, sk.get_support()) if y==True]
    print '--- Selected Features ---\r\n'
    print sk.get_support(True), "\r\n", feature_list_new

    feature_list_scores = zip(feature_list, sk.scores_)
    feature_list_scores = sorted(feature_list_scores, key=lambda k: k[1],
                                 reverse=True)
    print '--- All Features ---'
    for item in feature_list_scores:
        print item[0], ": ", "{0:.4f}".format(item[1])

    return
    
# ------------------ MAIN -------------
if __name__ == '__main__':
    #pca_test()
    kbest_test()