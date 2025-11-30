from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_documents, name='search'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/add/', views.add_document, name='add_document'),
    path('document/<int:pk>/download/', views.download_document, name='download_document'),
    # админ-маршруты в главном urls.py
]