from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render

class MyLoginView(LoginView):
    template_name = 'admin/auth/login.html'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.context_data['errors'] = 'Incorrect login or password.'
        return response

    def form_valid(self, form):
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.template_name = 'admin/auth/login.html'
        return super().get(request, *args, **kwargs)
