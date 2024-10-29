# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 20:47:25 2024

@author: Анастасія
"""

from django.urls import path
from .views import LibraryViewSet, AuthorViewSet, BookViewSet, ReaderViewSet, BorrowHistoryList, BorrowHistoryDetail

urlpatterns = [
    path('libraries/', LibraryViewSet.as_view({'get': 'list', 'post': 'create'})),  # Список бібліотек
    path('libraries/<int:pk>/', LibraryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # Деталі конкретної бібліотеки
    path('authors/', AuthorViewSet.as_view({'get': 'list', 'post': 'create'})),  # Список авторів
    path('authors/<int:pk>/', AuthorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # Деталі конкретного автора
    path('books/', BookViewSet.as_view({'get': 'list', 'post': 'create'})),  # Список книг
    path('books/<int:pk>/', BookViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # Деталі конкретної книги
    path('readers/', ReaderViewSet.as_view({'get': 'list', 'post': 'create'})),  # Список читачів
    path('readers/<int:pk>/', ReaderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # Деталі конкретного читача
    path('borrow-history/', BorrowHistoryList.as_view()),  # Список історії позик
    path('borrow-history/<int:pk>/', BorrowHistoryDetail.as_view()),  # Деталі конкретної позики
]
