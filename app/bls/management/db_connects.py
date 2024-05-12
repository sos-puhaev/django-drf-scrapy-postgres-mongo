from pymongo import MongoClient
from dotenv import load_dotenv
import os
import psycopg2

class ConnectionDb:
    
    def __init__(self):
        # Mongo Auth
        self.host_mongo = os.getenv("MONGO_DB_HOST")
        self.username_mongo = os.getenv("MONGO_DB_USERNAME")
        self.password_mongo = os.getenv("MONGO_DB_PASSWORD")
        self.auth_source_mongo = os.getenv("MONGO_AUTH_DB")
        self.port_mongo = 27017

        self.client = None
        self.db = None
        self.collection = None

        # Postgres Auth
        self.host_pg = os.getenv("POSTGRES_HOST")
        self.database_pg = os.getenv("POSTGRES_DB")
        self.user_pg = os.getenv("POSTGRES_USER")
        self.pass_pg = os.getenv("POSTGRES_PASSWORD")

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
