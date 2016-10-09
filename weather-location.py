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
        val = xml.split("<%s" % key)[1].split(">")[1].split("</")[0].strip()
        #val =  (xml.split("<%s>" % key)[1]).split("</")[0]
    except IndexError:
        return ""
    else:
        return val

def XMLdict(xml, keylist):
    #return a dictionary of values from XML string
    return {key: XMLval(xml, key) for key in keylist}

verbose = bool(1) ####
given = (len(sys.argv) > 1)
given = True ####

uname = "demo" #default user name, limited usage
try:
    with open("geonames") as f:
        uname = f.read().strip()
except IOError:
    pass

    
if verbose:
    print(uname)

if given:
    #use the given location string
#    arg = sys.argv[1]
    arg = "10006"
    arg = arg.replace(" ","%20").strip()
    if verbose:
        print( "Using given " + arg)
    
    #First do a smart search to find the place    
    url1 = "http://api.geonames.org/search?q=%s&maxRows=1&username=%s" % (arg,uname)
    content1=urlopen(url1).read()
    LAT = "lat"
    LON = "lng"
    CITY = "name"
    COUNTRY = "countryCode"
    #ZIP = "postalcode"
    if verbose:
        print(content1)
    loc_dict = XMLdict(content1,[LAT,LON,CITY,COUNTRY])
    geoID = XMLval(content1, "geonameId")
    
    #Now get more complete information to fill in the region/state and timezone    
    url2 = "http://api.geonames.org/get?geonameId=%s&username=%s" % (geoID,uname)
    content2 = urlopen(url2).read()
    REGION = "adminCode1"
    TIMEZONE = "timezone"
    loc_dict.update( XMLdict(content2,[REGION, TIMEZONE]) )
#    
#    lat = loc_dict[LAT]
#    lon = loc_dict[LON]
#    url3 = "http://api.geonames.org/timezone?lat=%s&lng=%s&username=%s" % (lat,lon,uname)
#    TIMEZONE = "timezoneId"
#    content3=urlopen(url3).read()
#    loc_dict.update( XMLdict(content3,[TIMEZONE]) )
    
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
loc_name = "%s, %s %s" % (loc_dict[CITY], loc_dict[REGION],
                             loc_dict[COUNTRY])
cfg_dict["lat"] = loc_dict[LAT]
cfg_dict["lon"] = loc_dict[LON]
cfg_dict["timezone"] = loc_dict[TIMEZONE]
cfg_dict["loc_name"] = loc_name
with open(cfg_file, "w") as f:
    for key in cfg_dict:
        f.write("%s=%s\n" % (key, cfg_dict[key]) )

#print the time zone
print(loc_dict[TIMEZONE])




