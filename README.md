# flask_ES


This small web app is built with flask, which shows the usage of elastic-search and mongodb with python.
It has a search functionality related to available data of all airports.


### Prerequisites


Flask, SQLAlchemy, PyMongo, Elasticsearch

### Installing

Create .env file with following variables:
SQLALCHEMY_URI = mysql://<user>:<pass>@<IP>/db
MONGO_URI = mongo-uri
SECRET_KEY = TOPSECRET
ELASTIC_URI = elasstic_search-url
ELASTIC_U = user
ELASTIC_P = pass


Create virtual env:
```
virtualenv -p python3.5 venv

source venv/bin/activate
```

Install requirements

```
pip install -r requirements
```

Create db 

```
mysql> CREATE DATABASE db_flask;
```

Migrate 

```
python> from app import db
python> db.create_all()

```
## Deployment

```
python app.py
```

## Built With

* [Flask](http://flask.pocoo.org/) - The python web framework
* [Elasticsearch](https://elasticsearch-py.readthedocs.io/en/master/) - Python ES client
* [MongoDB](https://flask-pymongo.readthedocs.io/en/latest/) - Flask Mongo client




