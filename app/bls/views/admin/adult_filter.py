import json
import re
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import psycopg2
from pymongo import MongoClient
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string



class AdultFilter(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/adult_filter.html'
    login_url = 'admin/'

    def get_context_data(self, **kwargs):
        
        items_per_page = int(self.request.GET.get('items_per_page', 10))
        page = self.request.GET.get('page', 1)

        show_context = list(self.show_adult_world())
    
        paginator = Paginator(show_context, items_per_page)
        try:
            torrents_page = paginator.page(page)
        except PageNotAnInteger:
            torrents_page = paginator.page(1)
        except EmptyPage:
            torrents_page = paginator.page(paginator.num_pages)

        adult_filter = super().get_context_data(**kwargs)
        adult_filter['adult_context'] = show_context
        adult_filter['adult_page'] = torrents_page
        adult_filter['paginator'] = items_per_page
        

        return adult_filter
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))

        dynamic_fields = data.get('dynamicFields', [])
        static_fields = data.get('staticFields', [])

        action_type = data.get('action_type', '')
        word = data.get('word', '')
        check = data.get('check', '')
        id = data.get('id', '')

        combined_static_fields = []
        combined_dynamic_fields = []

        for i in range(0, len(static_fields), 3):
            id_value = static_fields[i]['value']
            check_value = static_fields[i + 1]['value']
            word_value = static_fields[i + 2]['value']

            combined_static_item = {
                'id': id_value,
                'check': check_value,
                'word': word_value,
            }

            combined_static_fields.append(combined_static_item)

        if combined_static_fields:
            self.updateAdultFilter(combined_static_fields)

        for field in dynamic_fields:
            combined_dynamic_item = {
                'word': field.get('value', ''),
                'check': field.get('checkboxValue', ''),
            }

            combined_dynamic_fields.append(combined_dynamic_item)
        if combined_dynamic_fields:
            self.insertDynamicFieldAdultFulter(combined_dynamic_fields)
        
        if action_type == 'delete':
            if check == 1:
                check = 0
                self.search_and_change(word, check)
            elif check == 0:
                check = 1
                self.search_and_change(word, check)
            self.deleteWordAdultFilter(id)

        return JsonResponse({'status': 'success'})
    
    def deleteWordAdultFilter(self, id):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()
            delete_query = "DELETE FROM adult_filter WHERE id = %s;"
            cursor.execute(delete_query, (id,))
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            return False

    def insertDynamicFieldAdultFulter(self, dynamic_fields):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()

            for item in dynamic_fields:
                word_value = item.get('word', '')
                check_value = item.get('check', '')
                self.search_and_change(word_value, check_value)
                insert_query = f'INSERT INTO adult_filter (word, "check") VALUES (\'{word_value}\', {check_value});'
                cursor.execute(insert_query)

            connection.commit()
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Error: {e}")
            return False


    def updateAdultFilter(self, static_fields):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()

            for item in static_fields:
                id_value = item.get('id', '')
                word_value = item.get('word', '')
                check_value = item.get('check', '')
                self.search_and_change(word_value, check_value)
                update_query = f'UPDATE adult_filter SET word = \'{word_value}\', "check" = {check_value} WHERE id = {id_value};'

                cursor.execute(update_query)

            connection.commit()
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Error: {e}")
            return False

    def search_and_change(self, word, check):
        # set in .env
        client = MongoClient("mongo", username="user", password="password", authSource="mongo_db")
        db = client['mongo_db']
        collection = db['bls_scrapy']

        keywords = [word]
        regex_pattern = '|'.join(map(re.escape, keywords))

        if check == '0':
            result = collection.update_many(
                {"title": {"$regex": regex_pattern, "$options": "i"}},
                {"$set": {"adult": False}}
            )
        else:
            result = collection.update_many(
                {"title": {"$regex": regex_pattern, "$options": "i"}},
                {"$set": {"adult": True}}
            )


    def show_adult_world(self):
        try:
            # set in .env
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM adult_filter")
            show_word = cursor.fetchall()

            connection.commit()
            cursor.close()
            connection.close()

            return show_word
        except Exception as e:
            print(f"Error: {e}")
            return False

        