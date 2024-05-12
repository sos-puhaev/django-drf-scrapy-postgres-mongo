import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..management.db_connects import ConnectionDb

class MongoDataSerialListCreateView(APIView):
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
            # limit = int(request.GET.get('limit', 15))
            # offset = int(request.GET.get('offset', 0))
            imdb_id = request.GET.get('imdb_id', None)
            season = request.GET.get('season', None)
            resolution = request.GET.get('resolution', None)


            self.connection_db.connect_mongo()
            collection = self.connection_db.collection

            filter_condition = {'category': 'Series'}

            if imdb_id:
                if season is not None:
                    filter_condition['season'] = season
                torrents = self.search_serials_in_db(imdb_id, collection, filter_condition)
                
            return Response(torrents)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def search_serials_in_db(self, imdb_id, collection, filter_condition): # блок где происходит получение записей исходя из filter_condition
        title_search = collection.find_one({"imdb_id": imdb_id})
        if title_search:
            partial_title = title_search['title'][:4]
            filter_condition.update({"title": {"$regex": f"^{re.escape(partial_title)}"}}) # Добавляем условие
            results = collection.find(filter_condition)

            return self.convert_view_db_json(list(results))
        else:
            return []

    
    def convert_view_db_json(self, torrents):
        seasons = []
        # Перебираем каждую запись торрента
        for torrent in torrents:
            season_number = torrent['season']
            episode_number = torrent['episode']
            # Создаем словарь для хранения информации о серии
            episode_info = {
                '_id': str(torrent['id_torrent']),
                'title': torrent['title'],
                'season': season_number,
                'episode': episode_number,
                'imdb_id': torrent['imdb_id'],
                'resolution': torrent.get('quality', None),
                'size': int(torrent['size']),
                'category': torrent['category'],
                'sub_category': torrent['sub_category'],
                'link': torrent['url'],
                'peers': torrent['peers'],
                'seeds': torrent['seeds'],
                'is_verified': torrent['is_verified'],
                'date': torrent['date'],
                'date_sort': torrent['date_sort'],
                'adult': torrent['adult'],
                'source': torrent['source'],
                'magnet': torrent['magnet'],
                'num_comment': self.show_number_comment(str(torrent['id_torrent'])),
                'filename': torrent.get('filename', None),
            }
            found_season = False
            for season in seasons:
                if season['numberSeason'] == season_number:
                    # Проверяем, существует ли уже серия с таким номером
                    found_series = False
                    for series in season['series']:
                        if series['numberSeries'] == str(episode_number):
                            series['torrents'].append(episode_info)
                            found_series = True
                            break
                    if not found_series:
                        season['series'].append({
                            'numberSeries': str(episode_number),
                            'torrents': [episode_info]
                        })
                    found_season = True
                    break
            
            # Если сезон не найден, создаем новую запись о сезоне
            if not found_season:
                seasons.append({
                    'numberSeason': season_number,
                    'resolution': self.list_resolutions(torrents, season_number),
                    'series': [{
                        'numberSeries': str(episode_number),
                        'torrents': [episode_info]
                    }]
                })

        # Сортируем сезоны по номеру
        seasons = sorted(seasons, key=lambda x: int(x['numberSeason']))

        # Сортируем серии внутри каждого сезона по номеру
        for season in seasons:
            season['series'] = sorted(season['series'], key=lambda x: int(x['numberSeries']))

        return seasons

    def _in_dictionary_quality(self, quality):
        total_quality = ['Other', '1080p', '720p', '480p']
        for data in total_quality:
            if data == quality:
                if data == 'Other':
                    return data
                elif data == '1080p':
                    data = 'Full HD (1080p)'
                    return data
                elif data == '720p':
                    data = 'HD (720p)'
                    return data
                elif data == '480p':
                    data = 'SD (480p)'
                    return data
                else:
                    return quality
        return 'No quality'

    def list_resolutions(self, torrents, season_number):
        all_res = []
        for document in torrents:
            if document.get("season") == season_number:
                if "quality" in document:
                    document["quality"] = self._in_dictionary_quality(document["quality"])
                    all_res.append(document["quality"])
        unique_res = list(set(all_res))
        return unique_res