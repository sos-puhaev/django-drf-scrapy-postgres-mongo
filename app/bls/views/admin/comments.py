from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from ...management.db_connects import ConnectionDb

class ListComments(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/comments.html'
    login_url = 'admin/'

    def __init__(self):
        self.connection_db = ConnectionDb()

    def get_context_data(self, **kwargs):
        self.connection_db.connect_mongo()
        collection = self.connection_db.collection

        items_per_page = int(self.request.GET.get('items_per_page', 4))
        page = int(self.request.GET.get('page', 1))

        title_search = self.request.GET.get('q')
        itemId = self.request.GET.get('itemId', None)
        delete_comments = self.request.GET.get('flag', 'w')
        id_comments = self.request.GET.getlist('id_comments[]')

        total_items = collection.count_documents({})
        total_pages = total_items // items_per_page
        if total_items % items_per_page != 0:
            total_pages += 1
        offset = (page - 1) * items_per_page

        torrent_id = self.get_torrent_id()
        object_ids = [str(id_str) for id_str in torrent_id]
        
        cursor = collection.find({"id_torrent": {"$in": object_ids}}).skip(offset).limit(items_per_page)

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
                "id_torrent": {"$in": object_ids}
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
            title_context['total_pages'] = total_pages

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
        context['total_pages'] = total_pages

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            ajax_type = self.request.GET.get('ajax_type', None)

            if ajax_type == 'get_comment':
                response_data = self.get_response_comment(context)
                return JsonResponse(response_data)

            serialized_data = [
                {'id_torrent': str(item['id_torrent']), 'title': item['title'], 'adult': item['adult']}
                for item in context['comment_page']
            ]

            response_data = {
                'comment_page': serialized_data,
                'total_pages': context['total_pages'],
                'items_per_page': context['items_per_page'],
            }
            return JsonResponse(response_data)
        else:
            return super().render_to_response(context, **response_kwargs)

    def delete_comments_method(self, id_comments):
        id_comments = [int(id_comment) for id_comment in id_comments]
        print(id_comments)
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor
            delete_query = f"DELETE FROM bls_scrapy WHERE id = ANY(ARRAY[{id_comments}]);"
            
            cursor.execute(delete_query)
            self.connection_db.connection.commit()          
            cursor.close()

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
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("SELECT id, name, email, data_comment, comments, id_torrent FROM bls_scrapy WHERE id_torrent = %s ORDER BY data_comment;", (id,))

            columns = [desc[0] for desc in cursor.description]
            comment = [dict(zip(columns, row)) for row in cursor.fetchall()]

            cursor.close()
            self.connection_db.cursor.close()
            return comment

        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_torrent_id(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor

            cursor.execute("SELECT id_torrent FROM bls_scrapy;")
            self.connection_db.connection.commit() 

            torrent_id = [row[0] for row in cursor.fetchall()]
            cursor.close()
            self.connection_db.cursor.close()

            return torrent_id

        except Exception as e:
            print(f"Error: {e}")
            return []





        

