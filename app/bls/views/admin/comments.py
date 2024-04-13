from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import psycopg2
from pymongo import MongoClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from bson import ObjectId


class ListComments(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/comments.html'
    login_url = 'admin/'

    def get_context_data(self, **kwargs):
        # set in .env
        client = MongoClient("mongo", username="user", password="password", authSource="mongo_db")
        db = client['mongo_db']
        collection = db['bls_scrapy']

        items_per_page = int(self.request.GET.get('items_per_page', 4))
        page = self.request.GET.get('page', 1)
        title_search = self.request.GET.get('q')
        itemId = self.request.GET.get('itemId', None)
        delete_comments = self.request.GET.get('flag', 'w')
        id_comments = self.request.GET.getlist('id_comments[]')

        torrent_id = self.get_torrent_id()
        object_ids = [ObjectId(id_str) for id_str in torrent_id]
        cursor = collection.find({"_id": {"$in": object_ids}})

        if delete_comments == 'delete':
            self.delete_comments_method(id_comments)

        if itemId:
            comment = self.get_comment_show(itemId)
            comment_list = list(comment)
            paginator = Paginator(comment_list, items_per_page)

            try:
                torrent_data = paginator.page(page)
            except PageNotAnInteger:
                torrent_data = paginator.page(1)
            except EmptyPage:
                torrent_data = paginator.page(paginator.num_pages)

            comment_context = super().get_context_data(**kwargs)
            comment_context['comment_page'] = torrent_data
            comment_context['items_per_page'] = items_per_page
            return comment_context
            
        
        if title_search:
            title_filter = {
                "title": {'$regex': title_search, '$options': 'i'},
                "_id": {"$in": object_ids}
            }
            torrents_data = collection.find(title_filter)
            torrents_list = list(torrents_data)

            paginator = Paginator(torrents_list, items_per_page)
            try:
                torrent_data = paginator.page(page)
            except PageNotAnInteger:
                torrent_data = paginator.page(1)
            except EmptyPage:
                torrent_data = paginator.page(paginator.num_pages)

            title_context = super().get_context_data(**kwargs)
            title_context['comment_page'] = torrent_data
            title_context['items_per_page'] = items_per_page

            return title_context


        torrent_data = list(cursor)
        paginator = Paginator(torrent_data, items_per_page)
        try:
            torrent_data = paginator.page(page)
        except PageNotAnInteger:
            torrent_data = paginator.page(1)
        except EmptyPage:
            torrent_data = paginator.page(paginator.num_pages)

        context = super().get_context_data(**kwargs)
        context['comment_page'] = torrent_data
        context['items_per_page'] = items_per_page

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            ajax_type = self.request.GET.get('ajax_type', None)

            if ajax_type == 'get_comment':
                response_data = self.get_response_comment(context)
                return JsonResponse(response_data)

            serialized_data = [
                {'_id': str(ObjectId(item['_id'])), 'title': item['title'], 'adult': item['adult']}
                for item in context['comment_page']
            ]

            response_data = {
                'comment_page': serialized_data,
                'total_pages': context['comment_page'].paginator.num_pages,
                'items_per_page': context['items_per_page'],
            }
            return JsonResponse(response_data)
        else:
            return super().render_to_response(context, **response_kwargs)

    def delete_comments_method(self, id_comments):
        id_comments = [int(id_comment) for id_comment in id_comments]
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()
            delete_query = f"DELETE FROM bls_scrapy WHERE id = ANY(ARRAY[{id_comments}]);"

            cursor.execute(delete_query)
            connection.commit()

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_response_comment(self, context):
        serialized_data = [
            {'id': item['id'], 'name': item['name'], 'email': item['email'], 'data_comment': item['data_comment'], 'comments': item['comments']}
            for item in context['comment_page']
        ]

        response_data = {
            'comment_page': serialized_data,
            'total_pages': context['comment_page'].paginator.num_pages,
            'items_per_page': context['items_per_page'],
        }
        return response_data

    def get_comment_show(self, id):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )

            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email, data_comment, comments, id_torrent FROM bls_scrapy WHERE id_torrent = %s ORDER BY data_comment;", (id,))

            columns = [desc[0] for desc in cursor.description]
            comment = [dict(zip(columns, row)) for row in cursor.fetchall()]

            cursor.close()
            connection.close()

            return comment

        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_torrent_id(self):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )

            cursor = connection.cursor()
            cursor.execute("SELECT id_torrent FROM bls_scrapy;")

            torrent_id = [row[0] for row in cursor.fetchall()]
            cursor.close()
            connection.close()

            return torrent_id

        except Exception as e:
            print(f"Error: {e}")
            return []





        

