import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
from rest_framework.permissions import IsAuthenticated
import psycopg2
import pymongo
import re

class MongoDataListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def show_number_comment(self, id):
        # set in .env
        connection = psycopg2.connect(
            host = "postgres",
            database = "postgres",
            user = "app_db_user",
            password = "supersecretpassword"
        )
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(comments) FROM bls_scrapy WHERE id_torrent = %s", (id,))
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            return 0
        finally:
            cursor.close()
            connection.close()

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 15))
            offset = int(request.GET.get('offset', 0))
            title = request.GET.get('title', None)
            category = request.GET.get('category', None)
            is_verified = request.GET.get('is_verified', None)
            adult = request.GET.get('adult', None)
            sort_seeds = request.GET.get('sort_seeds', None)
            sort_peers = request.GET.get('sort_peers', None)
            sort_date = request.GET.get('sort_date', None)
            sort_title = request.GET.get('sort_title', None)
            spacing = request.GET.get('spacing', None)
            imdb_id = request.GET.get('imdb_id', None)

            # set in .env
            client = MongoClient("mongo", username="user", password="password", authSource="mongo_db")
            db = client['mongo_db']
            collection = db['bls_scrapy']

            filter_conditions = {}

            if imdb_id:
                filter_conditions['imdb_id'] = imdb_id

            if title:
                if title[0] == '[' or title[0] == '(':
                    new_string = title[1:]
                    filter_conditions['title'] = {'$regex': re.escape(new_string), '$options': 'i'}
                else:
                    start_index = re.search(r'[\(\[]', title)
                    if start_index:
                        st = start_index.start()
                        new_string = title[:st].strip()
                        filter_conditions['title'] = {'$regex': re.escape(new_string), '$options': 'i'}
                    else:
                        filter_conditions['title'] = {'$regex': re.escape(title), '$options': 'i'}
            
            if category and category.strip():
                filter_conditions['category'] = {'$regex': category, '$options': 'i'}

            if is_verified == 'true':
                filter_conditions['is_verified'] = True
            
            if adult == 'true':
                filter_conditions['adult'] = True

            sort_criteria = []
            if sort_seeds == 'up':
                sort_criteria.append(("seeds", pymongo.ASCENDING))
            elif sort_seeds == 'down':
                sort_criteria.append(("seeds", pymongo.DESCENDING))

            if sort_peers == 'up':
                sort_criteria.append(("peers", pymongo.ASCENDING))
            elif sort_peers == 'down':
                sort_criteria.append(("peers", pymongo.DESCENDING))

            if sort_date == 'up':
                sort_criteria.append(("date_sort", pymongo.ASCENDING))
            elif sort_date == 'down':
                sort_criteria.append(("date_sort", pymongo.DESCENDING))

            if spacing == '24h':
                start_timestamp_24h = time.time() - 24 * 60 * 60
                filter_conditions['date_sort'] = {'$gte': start_timestamp_24h}
            elif spacing == '1w':
                start_datetime_1w = time.time() - 7 * 24 * 60 * 60
                filter_conditions['date_sort'] = {'$gte': start_datetime_1w}
            elif spacing == '1y':
                start_datetime_1y = time.time() - 365 * 24 * 60 * 60
                filter_conditions['date_sort'] = {'$gte': start_datetime_1y}
            elif spacing == 'last':
                start_datetime_2y = time.time() - 2 * 365 * 24 * 60 * 60
                filter_conditions['date_sort'] = {'$gte': start_datetime_2y}

            if sort_title == 'up':
                sort_criteria.append(("title", pymongo.ASCENDING))
            elif sort_title == 'down':
                sort_criteria.append(("title", pymongo.DESCENDING))

            if sort_criteria:
                filter_document = collection.find(filter_conditions).sort(sort_criteria).skip(offset).limit(limit)
            else:
                filter_document = collection.find(filter_conditions).skip(offset).limit(limit)

            serialized_data_list = []

            for document in filter_document:
                serialized_data = {
                    '_id': str(document['_id']),
                    'title': document['title'],
                    'size': int(document['size']),
                    'category': document['category'],
                    'sub_category': document['sub_category'],
                    'link': document['url'],
                    'peers': document['peers'],
                    'seeds': document['seeds'],
                    'num_comment': self.show_number_comment(str(document['_id'])),
                    'is_verified': document['is_verified'],
                    'date': document['date'],
                    'date_sort': document['date_sort'],
                    'adult': document['adult'],
                    'source': document['source'],
                    'magnet': document['magnet'],
                    'episode': document.get('episode', None),
                    'season': document.get('season', None),
                    'imdb_id': document.get('imdb_id', None),
                    'quality': document.get('quality', None),
                    'filename': document.get('filename', None),
                    'small_screen': document.get('small_screen', None),
                    'large_screen': document.get('large_screen', None),
                }

                serialized_data_list.append(serialized_data)

            return Response(serialized_data_list)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

