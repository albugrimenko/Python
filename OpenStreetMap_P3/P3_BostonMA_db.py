# -*- coding: utf-8 -*-
import pprint
from pymongo import MongoClient

_MongoDB_Server_ = "mongodb://10.151.0.82:27017"

_FileName_Full_ = "./Data/Projects/boston_massachusetts.osm.ar.json"
_FileName_Sample_ = "./Data/Projects/boston_ma_sample.osm.50_ar.json"

#--- MongoDB
def dbTest():
    client = MongoClient(_MongoDB_Server_)
    db = client.test
    #db.test.insert_one({"test":"OK"})
    docs = db.test.find()
    for doc in docs:
        print doc

def get_db(db_name="OSM"):
    client = MongoClient(_MongoDB_Server_)
    db = client[db_name]
    return db

def get_collection(collection_name, db_name="OSM"):
    db = get_db(db_name)
    return db.get_collection(collection_name)

def run_aggregate(collection_name, pipeline, db_name="OSM", isPrint=True):
    col = get_collection(collection_name, db_name)
    data = [doc for doc in col.aggregate(pipeline)]
    if (isPrint):
        for doc in data:
            pprint.pprint(doc)
    return data
    
'''
def dbLoad(collectionName, jsonFileName):
    db = get_db()
    with open(jsonFileName) as f:
        data = json.loads(f.read())
        col = db.get_collection(collectionName)
        col.insert(data)
'''
#--- Basic Queries

def pipeline_nodetypecounts():
    pipeline = [ 
    {"$group": {"_id": "$node_type", 
                "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
    ]
    return pipeline

def pipeline_sourcecounts():
    pipeline = [ 
    {"$group": {"_id": "$source",
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
    ]
    return pipeline

def pipeline_source_MASS_counts():
    pipeline = [ 
    {"$match": {"source": {"$regex": "^(mass)"}}},
    {"$project": {
        "source": {"$substr": ["$source", 0, 7]}, 
        "node_type": "$node_type"
    }},
    {"$group": {"_id": {"source": "$source", "type" : "$node_type"},
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
    ]
    return pipeline

def pipeline_postcode_counts():
    pipeline = [ 
    {"$match": {"address.postcode": {"$exists": 1}, "address.city": {"$exists": 1}}},
    {"$group": {"_id": {"postcode": "$address.postcode", "city": "$address.city"},
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
    ]
    return pipeline

def pipeline_city_counts():
    pipeline = [ 
    {"$match": {"address.city": {"$exists": 1}}},
    {"$match": {"address.city": {"$regex": "Boston", "$options": "i"}}},
    {"$group": {"_id": "$address.city",
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 20}
    ]
    return pipeline

def pipeline_date_counts():
    pipeline = [ 
    {"$match": {"created.timestamp": {"$exists": 1}}},
    {"$project": {
        "date_year": {"$substr": ["$created.timestamp", 0, 4]}}
    },
    {"$group": {"_id": "$date_year",
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
    ]
    return pipeline

def pipeline_user_counts():
    pipeline = [ 
    {"$match": {"created.user": {"$exists": 1}}},
    {"$project": {
        "user": "$created.user", 
        "date_year": {"$substr": ["$created.timestamp", 0, 4]}
    }},
    {"$match": {"date_year": "2009"}},
    {"$group": {"_id": "$user",
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
    ]
    return pipeline

def pipeline_user_source2009_counts():
    pipeline = [ 
    {"$match": {"created.user": {"$exists": 1}}},
    {"$project": {
        "user": "$created.user", 
        "date_year": {"$substr": ["$created.timestamp", 0, 4]},
        "source" : "$source"
    }},
    {"$match": {"date_year": "2009", "user": "crschmidt"}},
    {"$group": {"_id": "$source",
                "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
    ]
    return pipeline
    
#------------------

if __name__ == '__main__':
    #dbTest()    # test MongoDB and ability to connect to it.
    
    #run_aggregate("Boston", pipeline_nodetypecounts())
    run_aggregate("Boston", pipeline_user_source2009_counts())
    
    print("--- DONE")