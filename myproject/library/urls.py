# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 20:47:25 2024

@author: Анастасія
"""

from django.urls import path
from .views import BookList, BookDetail, BookCreate, BookUpdate, BookDelete, AuthorCreateView,CategoryCreateView
from .views import LibraryViewSet, AuthorViewSet, BookViewSet, ReaderViewSet, BorrowHistoryList, BorrowHistoryDetail
from .views import viewer_list, delete_viewer
app_name = 'library'

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
    path('', BookList.as_view(), name='book_list'),  # Головна сторінка зі списком книг
    path('book/<int:pk>/', BookDetail.as_view(), name='book_detail'),  # Деталі книги
    path('book/add/', BookCreate.as_view(), name='book_add'),  # Форма для додавання книги
    path('book/edit/<int:pk>/', BookUpdate.as_view(), name='book_edit'),  # Форма для редагування книги
    path('book/delete/<int:pk>/', BookDelete.as_view(), name='book_delete'),
    path('author/create/<int:book_id>/', AuthorCreateView.as_view(), name='author_create'), # Додано book_id
    path('category/create/<int:book_id>/', CategoryCreateView.as_view(), name='category_create'),# Форма для видалення книги
    
    path('viewers/', viewer_list, name='viewer_list'),
    path('viewers/delete/<int:id>/', delete_viewer, name='delete_viewer'),
]
