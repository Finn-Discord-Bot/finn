from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy, DowngradingConsistencyRetryPolicy
from cassandra.query import tuple_factory
from time import strftime, localtime
import datetime
import json

with open('config/config.json', 'r') as config:
    conf = json.load(config)
    
cloud_config = {'secure_connect_bundle': conf['secure_connect_bundle']}
auth_provider = PlainTextAuthProvider(conf["CLIENT_ID"], conf["CLIENT_SECRET"]) # authenticate
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect('portfolios')  # select keyspace


# Adds a stock to a user's portfolio
def add_stock(uuid: int, ticker: str, qnty: float):
    session.execute(f"""
                    CREATE TABLE IF NOT EXISTS user{uuid} (
                        ticker text,
                        qnty double,
                        PRIMARY KEY (ticker, qnty)
                    )
                    """)
    session.execute(f"INSERT INTO user{uuid} (ticker, qnty) VALUES ('{ticker}', '{qnty}')")


# Remove a stock from a user's portfolio
def remove_stock(uuid: int, ticker: str):
    session.execute(f"""
                    DELETE FROM user{uuid}
                    WHERE ticker = {ticker} IF EXISTS
                    """)


# Pull Portfolio from user
def get_portfolio(uuid: int) -> dict:
    

