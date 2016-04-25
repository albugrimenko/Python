# -*- coding: utf-8 -*-
import sys
import codecs
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import json

# Original file downloaded from:
# https://mapzen.com/data/metro-extracts
# https://s3.amazonaws.com/metro-extracts.mapzen.com/boston_massachusetts.osm.bz2
_FileName_Full_ = "./Data/Projects/boston_massachusetts.osm"
_FileName_Sample_ = "./Data/Projects/boston_ma_sample.osm.50"
_FileName_Test_ = "./Data/Projects/boston_ma_sample.osm.11"

## for MongoDB
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)    # last word
street_type_mapping = { "St": "Street",
            "ST": "Street",
            "st": "Street",
            "St.": "Street",
            "St,": "Street",
            "street": "Street",
            "Street.": "Street",
            "ave": "Avenue",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Rd": "Road",
            "Rd.": "Road",
            "rd.": "Road",
            "Ct": "Court",
            "Pkwy": "Parkway",
            "Pl": "Place",
            "place": "Place",
            "Sq.": "Square"
            }

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

#---- helper functions
def check_re(value, reg):
    ''' returns True/False '''
    x = reg.search(value)
    return x

def print_sorted_dict(d, outstream=None):
    ''' sorts dictionary and prints its content '''
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        if (outstream is None):
            if (isInt(v) or isFloat(v)):
                print ("%s: %d" % (k, v))
            else:
                print ("%s:" % k)
                print (v)
        else:
            if (isInt(v) or isFloat(v)):
                outstream.write("%s: %d" % (k, v))
            else:
                outstream.write("%s:" % k)
                outstream.write(v)

def print_sorted_set(d, outstream=None):
    ''' sorts set and prints its content '''
    keys = sorted(d, key=lambda s: s.lower())
    if (outstream is None):
        print (", ".join(keys))
    else:
        outstream.write(", ".join(keys))
        outstream.write("\n")

def print_simple(d, outstream=None):
    if (outstream is None):
        print(d)
    else:
        outstream.write(d + "\n")

def isInt(v):
    try:
        int(v)
        return True
    except ValueError:
        return False
        
def isFloat(v):
    try:
        float(v)
        return True
    except ValueError:
        return False
    
def getType(v):
    v = v.strip()
    if (v == 'NULL'):
        return type(None)
    elif (v == ''):
        return type(None)
    elif v.startswith('{'):
        return type([])
    elif (isInt(v)):
        return type(1)
    elif (isFloat(v)):
        return type(1.1)
    else:
        return type("")

def getFloat(v):
    try:
        v = v.strip()
        return float(v)
    except ValueError:
        return None

#---- data transformation
def update_postcode(postcode):
    ''' Cleans up postal code '''
    new_code = postcode
    if postcode.find(" ", 0) > 0:
        new_code = postcode[postcode.find(" ", 0)+1:]
    elif postcode.find("-", 0) > 0:
        new_code = postcode[:postcode.find("-", 0)]
    
    if (not isInt(new_code)):
        new_code = ""
    return new_code
    
def update_streetname(name):
    ''' Clens up street name '''
    new_name = name
    m = street_type_re.search(new_name)
    if m:
        stype = m.group()
        if stype in street_type_mapping.keys():
            new_name = re.sub(street_type_re, street_type_mapping[stype], new_name)
    return new_name
    
def shape_element(element):
    ''' Shapes the xml element into JSON format '''
    node = {}
    node["created"] = {}
    node["address"] = {}
    if (element.tag == "node" or element.tag == "way"):
        lat = 0.0
        lon = 0.0
        node["node_type"] = element.tag
        for attr in element.attrib:
            if audit_CanNOTBeUsedAsKey(attr):
                # ignore
                continue
            elif (attr in CREATED):
                node["created"][attr] = element.attrib[attr]
            elif attr == "lat":
                lat = float(element.attrib[attr])
            elif attr == "lon":
                lon = float(element.attrib[attr])
            else:
                node[attr] = element.attrib[attr]
        
        if lat != 0 and lon != 0:
            node["pos"] = [lat, lon]
            
        for tag in element.iter("tag"):
            key = tag.attrib["k"].lower()
            if audit_CanNOTBeUsedAsKey(key):
                continue
            elif key == "address":
                node["address"]["fulladdress"] = tag.attrib["v"]
            elif key.startswith("addr:"):
                #if there is a second ":" that separates the type/direction of a street, the tag should be ignored
                if key.find(":", 5) < 0:
                    k = key[5:]
                    if len(k) < 1:
                        continue
                    if k in node["address"].keys():
                        print("-- Dupl address (%s): %s [id=%s]" % (k, tag.attrib["v"], element.attrib["id"]))
                    
                    v = tag.attrib["v"]
                    if (k == "street"):
                        v = update_streetname(v)
                    elif (k == "postcode"):
                        v = update_postcode(v)

                    if k in node["address"].keys():
                        node["address"][k] += " " + v
                    else:
                        node["address"][k] = v

            else:
                node[key] = tag.attrib["v"]
        
        for nd in element.iter("nd"):
            if "ref" in nd.attrib:
                if "node_refs" not in node.keys():
                    node["node_refs"] = []
                node["node_refs"].append(nd.attrib["ref"])
        
        if len(node["created"]) == 0:
            del node["created"]
        if len(node["address"]) == 0:
            del node["address"]
        return node
    else:
        return None

def osm_json(file_in, pretty = False, isWrapInArray=True):
    ''' Transforms osm file into JSON file
    if pretty = True then a nice looking indent will be added
    NOTE: set pretty = False to produce a file for MongoDB load.
    '''
    file_out = "{0}.json".format(file_in)
    #data = []
    with codecs.open(file_out, "w") as fo:
        if (isWrapInArray):
            fo.write("[\n")
        i = 0
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if (i > 0 and isWrapInArray):
                    fo.write(",")
                else:
                    i += 1

                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
        if (isWrapInArray):
            fo.write("\n]")
    return #data  

def osm_json_inChunks(file_in, chunk_rows=100000):
    ''' Transforms osm file into JSON file
    Do it in chunks where each file will have not more than chunk_rows elements
    File names are: <file_in>.json.1, <file_in>.json.2...
    '''
    chunk = 1
    i = 0
    fo = None
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            if (i == 0 or i >= chunk_rows):
                if fo:
                    fo.write("\n]")
                file_out = "{0}.json.{1}".format(file_in, chunk)    
                fo = codecs.open(file_out, "w")
                fo.write("[\n")
                chunk += 1
                i = 0
            else:
                fo.write(",\n")

            fo.write(json.dumps(el))
            i += 1
    return

def validate_jsonFile(jsonFileName):
    try:
        with open(jsonFileName) as f:
            json.loads(f.read())
        print('--- File %s is OK.' % jsonFileName)
        return True
    except:
        e = sys.exc_info()
        print('--- ERROR in File %s:' % jsonFileName)
        print (e)
        return False
        
#---- audit
def audit_CanNOTBeUsedAsKey(value):
    ''' Checks if the value can be used as a key and returns True or False'''
    return problemchars.search(value)

def audit_pos(source):
    ''' Audits geospatial coordinates and returns all wrong values '''
    minPos = [42.228, -71.191] # [minlat, minlon] from <bounds />
    maxPos = [42.42, -70.923] # [maxlat, maxlon] from <bounds />

    wrongType = { "lat": [], "lon": [] }
    outOfRange = { "lat": [], "lon": [] }
    for event, elem in ET.iterparse(source):
        if (elem.tag == "node" or elem.tag == "way"):
            lat = ""
            lon = ""
            for attr in elem.attrib:
                if attr == "lat":
                    lat = elem.attrib[attr]
                elif attr == "lon":
                    lon = elem.attrib[attr]
            # check the data
            if len(lat) > 0 and len(lon) > 0:
                if not isFloat(lat):
                    wrongType["lat"].append(lat)
                elif float(lat) < minPos[0] or float(lat) > maxPos[0]:
                    outOfRange["lat"].append(lat)
                if not isFloat(lon):
                    wrongType["lon"].append(lon)
                elif float(lon) < minPos[1] or float(lon) > maxPos[1]:
                    outOfRange["lon"].append(lon)
    return wrongType, outOfRange
    
def audit_street_type(source):
    ''' Audits all found street types '''
    street_type_expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", 
                            "Place", "Square", "Lane", "Road", "Trail", 
                            "Parkway", "Commons", "Terrace", "Artery", "Circle",
                            "Corner", "Park", "Row", "Turnpike", "Way", "Wharf"]    
    
    street_types = defaultdict(int)
    unexpected_street_types = defaultdict(int)
    for event, elem in ET.iterparse(source):
        if (elem.tag == "tag") and (elem.attrib['k'] == "addr:street"):
            street_name = elem.attrib['v']
            m = street_type_re.search(street_name)
            if m:        
                street_type = m.group()
                street_types[street_type] += 1
                if street_type in street_type_mapping.keys():
                    street_type = street_type_mapping[street_type]
                if street_type not in street_type_expected:
                    unexpected_street_types[street_type] += 1

    return street_types, unexpected_street_types
    
def audit(filename, audit_type):
    ''' Performes several types of basic audit based on audit_type:
    - StreetType - audits street types
    '''
    #with codecs.open(filename, encoding='utf-8', mode='r') as f:
    with open(filename, mode='r') as f:
        if (audit_type == "Pos"):
            wrongType, outOfRange = audit_pos(f)
            print("\n---- Pos has a wrong type:\n", wrongType)
            print("\n---- Pos out of range:\n", outOfRange)
        elif (audit_type == "StreetType"):
            street_types, streets_unexpected = audit_street_type(f)
            print_sorted_dict(street_types, None) 
            print("\n------ Unexpected street types -------")
            print_sorted_dict(streets_unexpected, None) 
            
            
            
#---- evaluation
def get_tags(source):
    ''' Gets distinct list of tags with count '''
    tags = defaultdict(int)
    for event, elem in ET.iterparse(source):
        tags[elem.tag] += 1
    return tags

def get_postcodes(source):
    ''' Gets distinct list of tags with count '''
    tags = defaultdict(int)
    for event, elem in ET.iterparse(source):
        if (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode"):
            postcode = update_postcode(elem.attrib['v'])
            tags[postcode] += 1
       
    return tags
    
def get_structure(source):
    ''' Gets simple structure of the file:
    - all elements with count
    - a distinct list of attributes 
    - a distinct list of child nodes 
    - distinct list of <tag k values
    '''
    nodes = defaultdict(dict)
    for _, element in ET.iterparse(source):
        k = element.tag
        if element.tag in nodes:
            nodes[k]["Count"] += 1
        else:
            nodes[k]["Count"] = 1
            nodes[k]["attrib"] = set()
            nodes[k]["children"] = set()
            nodes[k]["tag"] = defaultdict(int)
        for attr_name in element.attrib:
            nodes[k]["attrib"].add(attr_name)
            if k == "tag" and attr_name == "k":
                nodes[k]["tag"][element.attrib[attr_name]] += 1
        children = list(element) #element.getchildren()
        if children != None:
            for child in children:
                nodes[k]["children"].add(child.tag)
    return nodes

def print_structure(source, fileToSave=""):  
    ''' IF fileToSave provided, results will be stored in the file;
        otherwise printed to console
    '''
    nodes = get_structure(source)
    # print results        
    #with open(fileToSave, 'w') as fout:
    if (len(fileToSave) > 0):
        fout = open(fileToSave, 'w')
    else:
        fout = None
    keys = nodes.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = nodes[k]
        print_simple("\n===== {0} [{1}] =====".format(k, v["Count"]), fout)
        if (len(v["children"]) > 0):
            print_simple("--- children nodes:", fout)
            print_sorted_set(v["children"], fout)
        if (len(v["attrib"]) > 0):
            print_simple("--- attributes:", fout)
            print_sorted_set(v["attrib"], fout)
        if (len(v["tag"]) > 0):
            print_simple("--- tag attrib:k values:", fout)
            tk = sorted(v["tag"].keys(), key=lambda s: s.lower())
            for tkk in tk:
                print_simple("\t{0} [{1}]".format(tkk, v["tag"][tkk]), fout)
    if (len(fileToSave) > 0):
        print('-- structure description is ready: %s.' % fileToSave)
    return nodes

def evaluate(filename, eval_type):
    ''' Performes several types of basic evaluation based on eval_type:
    - GetTags - gets distinct list of tags with count
    - GetStruct - gets simple structure of the file
    '''
    #with codecs.open(filename, encoding='utf-8', mode='r') as f:
    with open(filename, mode='r') as f:
        if (eval_type == "GetTags"):
            tags = get_tags(f)
            print (tags)
        elif (eval_type == "GetStruct"):
            #nodes = get_structure(f, False, './Data/Projects/boston_ma_struc.txt')
            print_structure(f, '')
        elif (eval_type == "GetPostcodes"):
            tags = get_postcodes(f)
            print_sorted_dict(tags, None)


#-------------------
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag
    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def get_samplefile(sourceFile, sampleFile, sizeRatio=10):
    print('Getting every %ith element\nfrom %s\nto %s.%s.' % (sizeRatio, sourceFile, sampleFile, sizeRatio))
    with open(sampleFile + "." + str(sizeRatio), 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')
        
        # Write every 10th top level element
        for i, element in enumerate(get_element(sourceFile)):
            if i % sizeRatio == 0:
                output.write(ET.tostring(element, encoding='utf-8'))
                
        output.write('</osm>')
    print('--- Sample file is ready ---')

#------------------

if __name__ == '__main__':
    #get_samplefile(_FileName_Full_, _FileName_Sample_, 70)
    #evaluate(_FileName_Sample_, "GetPostcodes")     # GetTags, GetStruct, GetPostcodes
    #audit(_FileName_Sample_, "Pos")  # StreetType, Pos

    # get JSON     
    osm_json(_FileName_Sample_, False, False)
    #print("--- OSM -> JSON - DONE. ---")
    #validate_jsonFile("{0}.json".format(_FileName_Full_))
    #osm_json_inChunks(_FileName_Full_)

    print("--- DONE")