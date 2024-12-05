from django.urls import path
from . import  views

urlpatterns = [

    path('monthly-borrow-trends/', views.borrow_trends_view, name='monthly_borrow_trends'),
    path('reader-activity/', views.reader_activity_view, name='reader_activity'),
    path('borrow-counts-by-gender/', views.pie_chart_view, name='borrow_counts_by_gender'),
    path('top-readers/<int:author_id>/', views.top_readers_view, name='top_readers_by_author'),
    path('reader-ranking/<int:category_id>/', views.reader_ranking_view, name='reader_ranking'),
    path('average-borrows/', views.average_borrows_view, name='average_borrows_view'),
]

