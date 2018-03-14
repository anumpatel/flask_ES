import json
import urllib2
from bs4 import BeautifulSoup

def create_body(filename):
    insert_data = []
    with open('airports.json','r') as target:
        data = json.load(target)
    for d in data:
        operarion = {
            "index":{
                "_index" : "airport_data",
                "_type" : "airport",
                "_id" : str(d["_id"])
            }
        }
        data_dict = {
            "country": str(d["country"]),
            "city": str(d["city"]),
            "airport": str(d["airport"]),
            "iso": str(d["iso"]),
        }
        insert_data.append(operarion)
        insert_data.append(data_dict)

    return insert_data

def build_response_dict(es_response):
    if len(es_response['hits']['hits']) > 0:
        response_dict = []
        for d in es_response['hits']['hits']:
            x = d['_source']
            x['_id'] = d['_id']
            response_dict.append(x)
        return response_dict
    else:
        return None
    pass

def scrap_airports():
    data =urllib2.urlopen('https://en.wikipedia.org/wiki/List_of_international_airports_by_country')
    soup = BeautifulSoup(data, "lxml")

        
    table = soup.find_all('table')[0] 
    fl = open('airports.csv','a')
    fl.write(""""country","city","airport","iso"\n""")

    country = ''
    for table in soup.find_all('table'):
        for it, row in enumerate(table.find_all('tr')):
            columns = row.find_all('td')
            if len(columns) == 1:
                is_country = True
            else:
                is_country = False        
            for itr,column in enumerate(columns):
                if is_country:
                    country = column.get_text()
                else:
                    if itr == 0:
                        city = column.get_text()
                    elif itr == 1:
                        airport = column.get_text()
                    elif itr == 2:
                        iso = column.get_text()
                        try:
                            fl.write(u""""{0}","{1}","{2}","{3}"\n""".format(country, city, airport, iso))
                        except UnicodeEncodeError:
                            print(u""""{0}","{1}","{2}","{3}" """.format(country, city, airport, iso))
