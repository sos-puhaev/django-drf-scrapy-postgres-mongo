from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from datetime import datetime
from ...management.db_connects import ConnectionDb

class TorrentsDelete(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/torrents_delete.html'
    login_url = 'admin/'

    def __init__(self):
        self.connection_db = ConnectionDb()

    def post(self, request, *args, **kwargs):
        form_1 = self.request.POST.get('form1')
        form_2 = self.request.POST.get('form2')
        
        self.connection_db.connect_mongo()
        collection = self.connection_db.collection
        
        if form_1 == 'form1':
            links_to_delete = self.request.POST.getlist('links[]')
            try:
                result = collection.delete_many({'url': {'$in': links_to_delete}})
            except Exception as e:
                print(f'Error deleting documents: {e}')
        
            response_data = {'success': True, 'message': f'Deleted {result.deleted_count} torrents.'}
            return JsonResponse(response_data)
        
        elif form_2 == 'form2':
            dateFrom = datetime.strptime(self.request.POST.get('dateFrom'), "%Y-%m-%d").timestamp()
            dateUntil = datetime.strptime(self.request.POST.get('dateUntil'), "%Y-%m-%d").timestamp()
            seedsFrom = int(self.request.POST.get('seedsFrom')) if self.request.POST.get('seedsFrom') else None
            seedsUntil = int(self.request.POST.get('seedsUntil')) if self.request.POST.get('seedsUntil') else None
            peersFrom = int(self.request.POST.get('peersFrom')) if self.request.POST.get('peersFrom') else None
            peersUntil = int(self.request.POST.get('peersUntil')) if self.request.POST.get('peersUntil') else None
            
            if dateFrom > dateUntil:
                response_data = {'error': True, 'data_error': 'Date From is greater than Date Until'}
                return JsonResponse(response_data)
            
            query = {'date_sort': {'$gte': dateFrom, '$lte': dateUntil}}
            
            if seedsFrom is not None and seedsUntil is not None:
                query['seeds'] = {'$gte': seedsFrom, '$lte': int(seedsUntil)}
            
            if peersFrom is not None and peersUntil is not None:
                query['peers'] = {'$gte': peersFrom, '$lte': int(peersUntil)}
            
            result = collection.delete_many(query)

            response_data = {'success': True, 'message': f'Deleted {result.deleted_count} torrents.', 'deleted_count': result.deleted_count}
            return JsonResponse(response_data)
