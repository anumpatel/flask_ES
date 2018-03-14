import json


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