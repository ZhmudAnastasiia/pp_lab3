from django.urls import path
from .views import BookList, BookDetail, BookCreate, BookUpdate, BookDelete, AuthorCreateView,CategoryCreateView
from .views import LibraryViewSet, AuthorViewSet, BookViewSet, ReaderViewSet, BorrowHistoryList, BorrowHistoryDetail
from .views import viewer_list, delete_viewer
from . import views
from .views import (MonthlyBorrowTrendsByCategoryAPIView, ReaderActivityDurationAPIView,BorrowsCountByGenderAPIView,TopReadersForAuthorAPIView,ReaderRankingByCategoryAPIView,AverageBorrowsPerReaderInLibraryAPIView, CategoryStatsAPIView,CategoryStatsAPIViewPandas,BorrowDateStatsForReaderAPIView, BorrowDateStatsForReaderAPIViewPandas,CityBorrowStatsAPIView,CityBorrowStatsAPIViewPandas,LibraryBorrowStatsAPIView, LibraryBorrowStatsAPIViewPandas)
app_name = 'library'

urlpatterns = [
    path('libraries/', LibraryViewSet.as_view({'get': 'list', 'post': 'create'})),  
    path('libraries/<int:pk>/', LibraryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  
    path('authors/', AuthorViewSet.as_view({'get': 'list', 'post': 'create'})), 
    path('authors/<int:pk>/', AuthorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})), 
    path('books/', BookViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('books/<int:pk>/', BookViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  
    path('readers/', ReaderViewSet.as_view({'get': 'list', 'post': 'create'})),  
    path('readers/<int:pk>/', ReaderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})), 
    path('borrow-history/', BorrowHistoryList.as_view()), 
    path('borrow-history/<int:pk>/', BorrowHistoryDetail.as_view()),  
    path('', BookList.as_view(), name='book_list'), 
    path('book/<int:pk>/', BookDetail.as_view(), name='book_detail'),  
    path('book/add/', BookCreate.as_view(), name='book_add'), 
    path('book/edit/<int:pk>/', BookUpdate.as_view(), name='book_edit'),  
    path('book/delete/<int:pk>/', BookDelete.as_view(), name='book_delete'),
    path('author/create/<int:book_id>/', AuthorCreateView.as_view(), name='author_create'), 
    path('category/create/<int:book_id>/', CategoryCreateView.as_view(), name='category_create'),
    
    path('query-results/', views.display_statistics, name='query_results'),
    path('experiment/', views.experiment_view, name='experiment_view'),
    path('experiment1/', views.experiment_view1, name='experiment_results'),
    
    path('monthly-borrow-trends/', MonthlyBorrowTrendsByCategoryAPIView.as_view(), name='monthly-borrow-trends'),
    path('reader-activity-duration/', ReaderActivityDurationAPIView.as_view(), name='reader-activity-duration'),
    path('borrows-count-by-gender/', BorrowsCountByGenderAPIView.as_view(), name='borrows-count-by-gender'),
    path('top-readers-for-author/<int:author_id>/', TopReadersForAuthorAPIView.as_view(), name='top-readers-for-author'),
    path('reader-ranking-by-category/<int:category_id>/', ReaderRankingByCategoryAPIView.as_view(), name='reader-ranking-by-category'),
    path('average-borrows-per-reader-in-library/', AverageBorrowsPerReaderInLibraryAPIView.as_view(), name='average-borrows-per-reader-in-library'),

    path('library-stats/', LibraryBorrowStatsAPIView.as_view(), name='library-borrow-stats'),
    path('library-stats-pandas/', LibraryBorrowStatsAPIViewPandas.as_view(), name='library-borrow-stats-pandas'),
    path('city-stats/', CityBorrowStatsAPIView.as_view(), name='city-stats'),
    path('city-stats-pandas/', CityBorrowStatsAPIViewPandas.as_view(), name='city-stats-pandas'),
    path('reader/<int:reader_id>/borrow-date-stats/', BorrowDateStatsForReaderAPIView.as_view(), name='borrow_date_stats_reader'),
    path('reader/<int:reader_id>/borrow-date-stats-pandas/', BorrowDateStatsForReaderAPIViewPandas.as_view(), name='borrow_date_stats_reader_pandas'),
    path('category-stats/', CategoryStatsAPIView.as_view(), name='category_stats'),
    path('category-stats-pandas/', CategoryStatsAPIViewPandas.as_view(), name='category_stats_pandas'),
    path('book-publication-year-statistics/', views.book_publication_year_statistics, name='book_publication_year_statistics'),
    path('book-category-statistics-pandas/', views.book_category_statistics_pandas, name='book_category_statistics_pandas'),
   
    path('viewers/', viewer_list, name='viewer_list'),
    path('viewers/delete/<int:id>/', delete_viewer, name='delete_viewer'),
]
