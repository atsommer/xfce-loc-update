#!/usr/bin/env python
"""
Copyright Ariel Sommer 2016
License: GNU GPL (https://www.gnu.org/licenses/gpl.txt)

Modifies the config file for the XFCE weather app
uses data from Ubuntu GeoIP or GeoNames.org

"""
import shutil
from collections import OrderedDict
import os
import sys
if sys.version_info.major == 3:
    from urllib.request import urlopen
elif sys.version_info.major == 2:
    from urllib2 import urlopen

def XMLval(xml, key):
    #return the value of the key using very simple XML parsing
    try:
        #val =  (xml.split("<%s>" % key)[1]).split("</%s>" % key)[0]
        val =  (xml.split("<%s>" % key)[1]).split("</")[0]
    except IndexError:
        return ""
    else:
        return val

def XMLdict(xml, keylist):
    #return a dictionary of values from XML string
    return {key: XMLval(xml, key) for key in keylist}

verbose = bool(0)

if len(sys.argv) > 1:
    #use the given location string
    arg = sys.argv[1].replace(" ","").strip()
    if verbose:
        print( "Using given " + arg)
    url1 = "http://api.geonames.org/postalCodeSearch?placename=%s&maxRows=1&username=seventhsam" % arg
    LAT = "lat"
    LON = "lng"
    CITY = "name"
    COUNTRY = "countryCode"
    REGION = "adminCode1"
    ZIP = "postalcode"
    TIMEZONE = "timezoneId"
    
    content1=urlopen(url1).read()
    if verbose:
        print( content1)
    loc_dict1 = XMLdict(content1,[LAT,LON,CITY,COUNTRY,REGION,ZIP])
    
    lat = loc_dict1[LAT]
    lon = loc_dict1[LON]
    url2 = "http://api.geonames.org/timezone?lat=%s&lng=%s&username=seventhsam" % (lat,lon)
    content2=urlopen(url2).read()
    loc_dict2 = XMLdict(content2,[TIMEZONE])
    
    loc_dict = {}
    loc_dict.update(loc_dict1)
    loc_dict.update(loc_dict2)
    if verbose:
        print( loc_dict)
else:    
    
    file_like = urlopen("http://geoip.ubuntu.com/lookup")
    content = file_like.read()
    LAT = "Latitude"
    LON = "Longitude"
    CITY = "City"
    COUNTRY = "CountryCode3"
    REGION = "RegionCode"
    ZIP = "ZipPostalCode"
    TIMEZONE = "TimeZone"
    loc_dict = XMLdict(content,[LAT,LON,CITY,COUNTRY,REGION,ZIP,TIMEZONE])

#Modify the Weather settings file
cfg_file = os.path.expanduser("~/.config/xfce4/panel/weather-3.rc")

#0. make a backup copy
shutil.copyfile(cfg_file, cfg_file+".backup")

#1. read the file
cfg_dict=OrderedDict()
with open(cfg_file) as f:
    wrc_lines = f.readlines()
    for line in wrc_lines:
        line = line.strip()
        if line:
            #print( line)
            LHS, RHS = line.split("=",1)            
            cfg_dict[LHS] = RHS

#2. update the parameters
loc_name = "%s, %s %s %s" % (loc_dict[CITY], loc_dict[REGION],
                             loc_dict[ZIP], loc_dict[COUNTRY])
cfg_dict["lat"] = loc_dict[LAT]
cfg_dict["lon"] = loc_dict[LON]
cfg_dict["timezone"] = loc_dict[TIMEZONE]
cfg_dict["loc_name"] = loc_name
with open(cfg_file, "w") as f:
    for key in cfg_dict:
        f.write("%s=%s\n" % (key, cfg_dict[key]) )

#print the time zone
print(loc_dict[TIMEZONE])




