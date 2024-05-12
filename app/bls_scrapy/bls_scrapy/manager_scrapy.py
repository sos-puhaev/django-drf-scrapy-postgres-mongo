from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2

class ConnectionDbScrapy:
    
    def __init__(self):
        # Mongo Auth
        self.host_mongo = 'mongo'
        self.username_mongo = 'jonnijonni'
        self.password_mongo = 'abc234Def'
        self.auth_source_mongo = 'mongo_db'
        self.port_mongo = 27017

        self.client = None
        self.db = None
        self.collection = None

        # Postgres Auth
        self.host_pg = 'postgres'
        self.database_pg = 'app_db'
        self.user_pg = 'app_db_user'
        self.pass_pg = 'supersecretpassword'

        self.connection = None
        self.cursor = None

    def connect_mongo(self):
        try:
            self.client = MongoClient(host=self.host_mongo,
                                      port=self.port_mongo,
                                      username=self.username_mongo,
                                      password=self.password_mongo,
                                      authSource=self.auth_source_mongo)
            self.db = self.client['mongo_db']
            self.collection = self.db['bls_scrapy']

        except Exception as e:
            print("Error connecting to MongoDB:", e)

    def connect_pg(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host_pg,
                database='postgres',
                user=self.user_pg,
                password=self.pass_pg
            )
            self.cursor = self.connection.cursor()
            print("Successfully connected to PostgreSQL!")
        
        except Exception as e:
            print("Error connecting to PostgreSQL:", e)
