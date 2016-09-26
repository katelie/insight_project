from __future__ import print_function, division
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd

dbname = 'insight_project'
username = 'kateliea'

engine = create_engine('postgres://%s@localhost/%s' % (username, dbname))
print(engine.url)

if not database_exists(engine.url):
    create_database(engine.url)
print(database_exists(engine.url))
