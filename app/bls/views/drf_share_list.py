from bson import ObjectId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..management.db_connects import ConnectionDb

class ShareList(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        self.connection_db = ConnectionDb()

    def show_number_comment(self, id):
        self.connection_db.connect_pg()
        cursor = self.connection_db.cursor
        try:
            cursor.execute("SELECT COUNT(comments) FROM bls_scrapy WHERE id_torrent = %s", (id,))
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            return 0
        finally:
            cursor.close()
            self.connection_db.connection.close()

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 15))
            offset = int(request.GET.get('offset', 0))
            torrent_id = request.GET.get('torrent_id', None)

            self.connection_db.connect_mongo()
            collection = self.connection_db.collection

            filter_conditions = {}
            if torrent_id:
                filter_conditions['id_torrent'] = torrent_id
            else:
                return Response({"error": "torrent_id is not specified."})

            serialized_data_list = []
            filter_document = collection.find(filter_conditions).skip(offset).limit(limit)

            for document in filter_document:
                serialized_data = {
                    '_id': str(document['id_torrent']),
                    'title': document['title'],
                    'size': int(document['size']),
                    'category': document['category'],
                    'sub_category': document['sub_category'],
                    'link': document['url'],
                    'peers': document['peers'],
                    'seeds': document['seeds'],
                    'num_comment': self.show_number_comment(str(document['id_torrent'])),
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
