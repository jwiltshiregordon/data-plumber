import os

from django.conf import settings
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from main.views import format_builder_view, format_checker_view, parser_view, search_view

urlpatterns = [
    path('', TemplateView.as_view(template_name='main/landing.html'), name='home'),
    path('format-builder/', format_builder_view, name='format_builder'),
    path('format-checker/<uuid:check_uuid>/', format_checker_view, name='format_checker'),
    path('format-checker/<uuid:check_uuid>/parser/', parser_view, name='format_parser'),
    path('format-checker/', search_view, name='format_search')
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^vue/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, '../frontend/dist'),
        }),
        re_path(r'^pyodide/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, '../frontend/pyodide'),
        }),
    ]
