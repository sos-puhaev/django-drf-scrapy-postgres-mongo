from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import psycopg2
from pymongo import MongoClient
from django.http import JsonResponse
from django.template.loader import render_to_string

class BackupSetting(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboard/backup.html'
    login_url = 'admin/'