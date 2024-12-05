from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .NetworkHelper import NetworkHelper
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import BookForm
from .models import Library, Author, Book, Reader, BorrowHistory, BookCategory
from .serializer import LibrarySerializer, AuthorSerializer, BookSerializer, ReaderSerializer, BorrowHistorySerializer
import pandas as pd
from .queries import get_monthly_borrow_trends_by_category, reader_activity_duration, get_borrow_counts_by_gender, top_readers_for_author, get_reader_ranking_by_category,get_average_borrows_per_reader_in_library,execute_queries_parallel,run_experiment,perform_experiments,generate_execution_time_graph
from django.db.models import Avg, Min, Max,Count


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class ReaderViewSet(viewsets.ModelViewSet):
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer

class BorrowHistoryList(APIView):
    def get(self, request, format=None):
        borrow_history = BorrowHistory.objects.all()
        serializer = BorrowHistorySerializer(borrow_history, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BorrowHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BorrowHistoryDetail(APIView):
    def get_object(self, pk):
        try:
            return BorrowHistory.objects.get(pk=pk)
        except BorrowHistory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        borrow_record = self.get_object(pk)
        serializer = BorrowHistorySerializer(borrow_record)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        borrow_record = self.get_object(pk)
        serializer = BorrowHistorySerializer(borrow_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        borrow_record = self.get_object(pk)
        borrow_record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookList(ListView):
    model = Book
    template_name = 'library/home.html'
    context_object_name = 'books'

class BookDetail(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = self.object.authors.all()
        context['categories'] = self.object.categories.all()  
        return context
    
    def form_valid(self, form):
        book = form.save()
        authors = self.request.POST.getlist('authors')  
        book.authors.set(authors)  
        categories = self.request.POST.getlist('categories') 
        book.categories.set(categories)  
        return redirect('library:book_list')

class BookCreate(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        book = form.save(commit=False)
        book.save()

        authors = self.request.POST.getlist('authors')
        categories = self.request.POST.getlist('categories')

        book.authors.set(authors) 
        book.categories.set(categories) 

        return redirect('library:book_list')

class BookUpdate(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['authors'] = Author.objects.all()  
       context['categories'] = BookCategory.objects.all() 
       context['selected_authors'] = self.object.authors.all()  
       context['selected_categories'] = self.object.categories.all() 
       return context

    def form_valid(self, form):
        book = form.save()  

        authors = self.request.POST.getlist('authors')
        categories = self.request.POST.getlist('categories')

        book.authors.clear()
        book.authors.add(*[get_object_or_404(Author, id=author_id) for author_id in authors])

        book.categories.clear()
        book.categories.add(*[get_object_or_404(BookCategory, id=category_id) for category_id in categories])

        return redirect('library:book_detail', pk=book.id)
    
class BookDelete(DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:book_list') 


class AuthorCreateView(CreateView):
    model = Author
    template_name = 'library/author_form.html'
    fields = ['first_name', 'last_name', 'birth_year', 'death_year']

    def form_valid(self, form):
        form.save()
        return redirect('library:book_list')
    
class CategoryCreateView(CreateView):
    model = BookCategory
    template_name = 'library/category_form.html'  
    fields = ['name']  

    def form_valid(self, form):
        form.save()
        return redirect('library:book_list')  

def viewer_list(request):
    viewers = NetworkHelper.getlist('http://127.0.0.1:8001/api/viewers/')  
    return render(request, 'library/helper.html', {'viewers': viewers})

def delete_viewer(request, id):
    url = f'http://127.0.0.1:8001/api/viewers/{id}/' 
    NetworkHelper.delete(url)
    return redirect('library:viewer_list')  

def render_error(request, message):
    return render(request, 'library/plotly_dashboard.html', {'error': message})



def book_publication_year_statistics(request):
    stats = Book.objects.aggregate(
        avg_year=Avg('publication_year'),
        min_year=Min('publication_year'),
        max_year=Max('publication_year'),
    )

    books = Book.objects.all().order_by('publication_year')
    median_year = books[len(books) // 2].publication_year if len(books) % 2 != 0 else \
        (books[len(books) // 2 - 1].publication_year + books[len(books) // 2].publication_year) / 2
    
    stats['median_year'] = median_year

    return render(request, 'library/book_publication_year_statistics.html', {'stats': stats})

def book_category_statistics_pandas(request):
    books = Book.objects.all().values('categories__name', 'title')
    df = pd.DataFrame(books)

    stats = df.groupby('categories__name').agg(
        count=('title', 'count')
    ).reset_index()

    return render(request, 'library/book_category_statistics_pandas.html', {'stats': stats.to_dict(orient='records')})

class CategoryStatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        category_stats = BorrowHistory.objects.values('book__categories__name').annotate(
            avg_borrows=Avg('id'),  
            min_borrows=Min('id'), 
            max_borrows=Max('id'), 
            total_borrows=Count('id')
        )

        data = [
            {
                'category': stat['book__categories__name'],
                'avg_borrows': stat['avg_borrows'],
                'min_borrows': stat['min_borrows'],
                'max_borrows': stat['max_borrows'],
                'total_borrows': stat['total_borrows']
            }
            for stat in category_stats
        ]

        return Response(data)


class CategoryStatsAPIViewPandas(APIView):
    def get(self, request, *args, **kwargs):

        data = BorrowHistory.objects.all().values('book__categories__name', 'id')

        df = pd.DataFrame(data)

        category_stats = df.groupby('book__categories__name').agg(
            avg_borrows=('id', 'mean'),  
            median_borrows=('id', 'median'), 
            min_borrows=('id', 'min'),
            max_borrows=('id', 'max')  
        )

        result = category_stats.reset_index().to_dict(orient='records')

        return Response(result)

class BorrowDateStatsForReaderAPIView(APIView):
    def get(self, request, reader_id, *args, **kwargs):

        date_stats = BorrowHistory.objects.filter(reader_id=reader_id).aggregate(
            min_borrow_date=Min('borrow_date'),
            max_borrow_date=Max('borrow_date')
        )

        data = {
            'min_borrow_date': date_stats['min_borrow_date'],
            'max_borrow_date': date_stats['max_borrow_date'],
        }

        return Response(data)
    
class BorrowDateStatsForReaderAPIViewPandas(APIView):
    def get(self, request, reader_id, *args, **kwargs):
        data = BorrowHistory.objects.filter(reader_id=reader_id).values('borrow_date')

        df = pd.DataFrame(data)

        date_stats = df['borrow_date'].agg(['min', 'max'])

        result = {
            'min_borrow_date': date_stats['min'],
            'max_borrow_date': date_stats['max']
        }

        return Response(result)   
    
class CityBorrowStatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        reader_stats = (
            BorrowHistory.objects.values('reader__city', 'reader_id') 
            .annotate(total_borrows=Count('id')) 
        )

        city_totals = {}
        city_counts = {}

        for stat in reader_stats:
            city = stat['reader__city']
            if city not in city_totals:
                city_totals[city] = 0
                city_counts[city] = 0
            city_totals[city] += stat['total_borrows']
            city_counts[city] += 1

        city_stats = [
            {
                'city': city,
                'avg_borrows': city_totals[city] / city_counts[city],
            }
            for city in city_totals
        ]

        return Response(city_stats)

    
class CityBorrowStatsAPIViewPandas(APIView):
    def get(self, request, *args, **kwargs):

        data = list(
            BorrowHistory.objects.select_related('reader')
            .values('reader__city', 'reader_id')
            .annotate(total_borrows=Count('id'))
        )

        df = pd.DataFrame(data)

        if df.empty:
            return Response([])

        city_stats = (
            df.groupby('reader__city')['total_borrows']
            .mean()
            .reset_index()
            .rename(columns={'reader__city': 'city', 'total_borrows': 'avg_borrows'})
        )

        result = city_stats.to_dict(orient='records')

        return Response(result)
 
class LibraryBorrowStatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        library_stats = Library.objects.annotate(
            total_borrows=Count('librarymember__reader__borrowhistory')
        ).values('name', 'total_borrows')

        data = [
            {
                'library': stat['name'],
                'total_borrows': stat['total_borrows']
            }
            for stat in library_stats
        ]

        return Response(data)
    
class LibraryBorrowStatsAPIViewPandas(APIView):
    def get(self, request, *args, **kwargs):
        data = list(
            BorrowHistory.objects.select_related('reader__librarymember__library')
            .values('reader__librarymember__library__name')
            .annotate(total_borrows=Count('id'))
        )

        df = pd.DataFrame(data)

        if df.empty:
            return Response([])

        library_stats = (
            df.groupby('reader__librarymember__library__name')['total_borrows']
            .sum()
            .reset_index()
            .rename(columns={'reader__librarymember__library__name': 'library', 'total_borrows': 'total_borrows'})
        )

        result = library_stats.to_dict(orient='records')

        return Response(result)
    
    
    
class MonthlyBorrowTrendsByCategoryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        categories, months, borrow_counts = get_monthly_borrow_trends_by_category()

        df = pd.DataFrame({
            'Category': categories,
            'Month': months,
            'BorrowCount': borrow_counts
        })

        return Response(df.to_dict(orient='records'))

class ReaderActivityDurationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        reader_names, durations = reader_activity_duration()

        df = pd.DataFrame({
            'ReaderName': reader_names,
            'ActivityDuration': durations
        })

        return Response(df.to_dict(orient='records'))
    
class BorrowsCountByGenderAPIView(APIView):
    def get(self, request, *args, **kwargs):
        genders, borrow_counts = get_borrow_counts_by_gender()

        df = pd.DataFrame({
            'Gender': genders,
            'BorrowCount': borrow_counts
        })

        return Response(df.to_dict(orient='records'))

class TopReadersForAuthorAPIView(APIView):
    def get(self, request, author_id, *args, **kwargs):
        top_readers = top_readers_for_author(author_id)

        df = pd.DataFrame({
            'ReaderID': [reader.id for reader in top_readers],  # Використовуємо id
            'TotalBooksByAuthor': [reader.total_books_by_author for reader in top_readers]
        })

        return Response(df.to_dict(orient='records'))


class ReaderRankingByCategoryAPIView(APIView):
    def get(self, request, category_id, *args, **kwargs):
        reader_ranking = get_reader_ranking_by_category(category_id)

        df = pd.DataFrame({
            'ReaderID': [reader.id for reader in reader_ranking],  # Використовуємо id
            'TotalBorrows': [reader.total_borrows for reader in reader_ranking],
            'AvgBorrows': [reader.avg_borrows for reader in reader_ranking]
        })

        return Response(df.to_dict(orient='records'))


class AverageBorrowsPerReaderInLibraryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        library_data = get_average_borrows_per_reader_in_library()

        df = pd.DataFrame({
            'LibraryID': [library.id for library in library_data],  # Використовуємо id
            'AvgBorrowsPerReader': [library.avg_borrows_per_reader for library in library_data]
        })

        return Response(df.to_dict(orient='records'))

def display_statistics(request):
    result = execute_queries_parallel()

    return render(request, 'library/report_template.html', {'result': result})

def experiment_view(request):
    thread_count = 8
    execution_time, cpu_usage, memory_usage, results = run_experiment(thread_count)

    combined_results = []
    seen_categories = set()
    for result in results:
        for category, month, borrow_count in zip(*result):
            if category not in seen_categories:
                seen_categories.add(category)
                combined_results.append({
                    'category': category,
                    'month': month,
                    'borrow_count': borrow_count
                })

    context = {
        'execution_time': execution_time,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'combined_results': combined_results, 
    }

    return render(request, 'library/experiment_results.html', context)


def experiment_view1(request):
    thread_counts, execution_times = perform_experiments()

    combined_data = zip(thread_counts, execution_times)

    graph_html = generate_execution_time_graph(thread_counts, execution_times)

    context = {
        'graph_html': graph_html,
        'combined_data': combined_data,  
    }
    
    return render(request, 'library/experiment_result.html', context)
