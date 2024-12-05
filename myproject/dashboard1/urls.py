from django.urls import path
from . import views

urlpatterns = [
    path('average-borrows/',  views.average_borrows_graph_view, name='average_borrows_graph'),
    path('reader-ranking/<int:category_id>/', views.reader_ranking_graph_view, name='reader_ranking_graph'),
    path('top-readers/<int:author_id>/', views.top_readers_graph_view, name='top_readers_graph'),
    path('reader-activity/', views.reader_activity_graph_view, name='reader_activity_graph'),
    path('monthly_borrow_trends/', views.monthly_borrow_trends_by_category, name='monthly_borrow_trends'),
    path('borrows_by_gender/',  views.borrows_count_by_gender, name='borrows_by_gender'),
]