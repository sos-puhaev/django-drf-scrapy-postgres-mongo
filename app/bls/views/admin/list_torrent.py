from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import re
from urllib.parse import quote, unquote
from ...management.db_connects import ConnectionDb

class ListTorrent(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/list_torrent.html'
    login_url = 'admin/'

    def __init__(self):
        self.connection_db = ConnectionDb()

    def get_context_data(self, **kwargs):
        self.connection_db.connect_mongo()
        collection = self.connection_db.collection

        items_per_page = int(self.request.GET.get('items_per_page', 10))
        page = int(self.request.GET.get('page', 1))

        sort_order = self.request.GET.get('sort_order', 'def')
        sort_seeds = self.request.GET.get('sort_seeds', 'def')
        sort_peers = self.request.GET.get('sort_peers', 'def')
        sort_adult = self.request.GET.get('sort_adult', 'def')
        title_search = self.request.GET.get('q')
        delete_torrent = self.request.GET.get('flag', 'w')
        magnets = self.request.GET.getlist('magnets[]')

        total_items = collection.count_documents({})
        total_pages = total_items // items_per_page
        if total_items % items_per_page != 0:
            total_pages += 1
        offset = (page - 1) * items_per_page

        if delete_torrent == 'delete':
            self.deleting_torrents(magnets, collection)

        title_filter = {}
        if title_search:
            if title_search[0] == '[' or title_search[0] == '(':
                new_string = title_search[1:]
                title_filter['title'] = {'$regex': re.escape(new_string), '$options': 'i'}
            else:
                start_index = re.search(r'[\(\[]', title_search)
                if start_index:
                    st = start_index.start()
                    new_string = title_search[:st].strip()
                    title_filter['title'] = {'$regex': re.escape(new_string), '$options': 'i'}
                else:
                    title_filter['title'] = {'$regex': re.escape(title_search), '$options': 'i'}
            torrents_data = collection.find(title_filter)
            torrents_list = list(torrents_data)

            paginator = Paginator(torrents_list, items_per_page)
            try:
                torrents_page = paginator.page(page)
            except PageNotAnInteger:
                torrents_page = paginator.page(1)
            except EmptyPage:
                torrents_page = paginator.page(paginator.num_pages)

            title_context = super().get_context_data(**kwargs)
            title_context['torrents_page'] = torrents_page
            title_context['items_per_page'] = items_per_page
            title_context['total_pages'] = total_pages

            return title_context

        if sort_order == 'def':
            torrents_data = collection.find({}).skip(offset).limit(items_per_page)
        elif sort_order == 'asc':
            torrents_data = collection.find({}).sort('title', 1).skip(offset).limit(items_per_page)
        elif sort_order == 'desc':
            torrents_data = collection.find({}).sort('title', -1).skip(offset).limit(items_per_page)
            
        if sort_seeds == 'up':
            torrents_data = collection.find({}).sort('seeds', 1).skip(offset).limit(items_per_page)
        elif sort_seeds == 'down':
            torrents_data = collection.find({}).sort('seeds', -1).skip(offset).limit(items_per_page)

        if sort_peers == 'up':
            torrents_data = collection.find({}).sort('peers', 1).skip(offset).limit(items_per_page)
        elif sort_peers == 'down':
            torrents_data = collection.find({}).sort('peers', -1).skip(offset).limit(items_per_page)
        
        if sort_adult == 'up':
            torrents_data = collection.find({}).sort('adult', 1).skip(offset).limit(items_per_page)
        elif sort_adult == 'down':
            torrents_data = collection.find({}).sort('adult', -1).skip(offset).limit(items_per_page)

        torrents_list = list(torrents_data)

        paginator = Paginator(torrents_list, items_per_page)
        try:
            torrents_page = paginator.page(page)
        except PageNotAnInteger:
            torrents_page = paginator.page(1)
        except EmptyPage:
            torrents_page = paginator.page(paginator.num_pages)

        context = super().get_context_data(**kwargs)
        context['torrents_page'] = torrents_page
        context['items_per_page'] = items_per_page
        context['total_pages'] = total_pages

        return context
    
    def render_to_response(self, context, **response_kwargs):

        if self.request.is_ajax():
            serialized_data = [
            {'title': item['title'], 'seeds': item['seeds'], 'peers': item['peers'], 'adult': item['adult'], 'magnet': item['magnet']}
            for item in context['torrents_page']
            ]

            response_data = {
                'torrents_page': serialized_data,
                'total_pages': context['total_pages'],
                #'total_pages': context['torrents_page'].paginator.num_pages,
                'items_per_page': context['items_per_page'],
            }
            return JsonResponse(response_data)
        else:
            return super().render_to_response(context, **response_kwargs)
        
    def deleting_torrents(self, torrents, collection):
        collection.delete_many({'magnet': {'$in': torrents}})
    
    def escape_char(self, str):
        special_characters = r'[]()'
        return re.sub(f'([{re.escape(special_characters)}])', r'\\\1', str)

