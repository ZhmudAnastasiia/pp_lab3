from django.db.models import FloatField, Avg, Max, Min,Count, When, IntegerField, Sum, F, Case, ExpressionWrapper, DurationField
from .models import Library, Reader, BookCategory
from django.db.models.functions import Greatest, Least, TruncMonth
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import psutil
import plotly.graph_objs as go

def get_monthly_borrow_trends_by_category():
    data = BookCategory.objects.annotate(
        month=TruncMonth('bookbycategory__book__borrowhistory__borrow_date')
    ).values(
        'name', 'month' 
    ).annotate(
        borrow_count=Count('bookbycategory__book__borrowhistory', distinct=True)
    ).order_by('month', 'name')

    categories = []
    months = []
    borrow_counts = []

    for entry in data:
        categories.append(entry['name'])
        months.append(entry['month'].strftime('%Y-%m'))
        borrow_counts.append(entry['borrow_count'])

    return categories, months, borrow_counts


def reader_activity_duration():
    readers = Reader.objects.annotate(
        first_borrow_date=Min('borrowhistory__borrow_date'),
        last_borrow_date=Max('borrowhistory__return_date'),
        activity_duration=ExpressionWrapper(
            Greatest(F('last_borrow_date'), F('first_borrow_date')) - 
            Least(F('first_borrow_date'), F('last_borrow_date')),
            output_field=DurationField()
        )
    ).order_by('-activity_duration')

    reader_names = []
    durations = []

    for reader in readers:
        if reader.activity_duration is not None:

            full_name = f"{reader.first_name} {reader.last_name}"
            reader_names.append(full_name)  
            durations.append(reader.activity_duration.days)  

    return reader_names, durations


def get_borrow_counts_by_gender():
    
    data = Reader.objects.annotate(
        male_borrows=Count(
            Case(
                When(gender='male', then=F('borrowhistory__id')),
                output_field=IntegerField()
            )
        ),
        female_borrows=Count(
            Case(
                When(gender='female', then=F('borrowhistory__id')),
                output_field=IntegerField()
            )
        ),
    ).aggregate(
        male_count=Sum('male_borrows'),
        female_count=Sum('female_borrows')
    )

    male_count = data['male_count'] or 0
    female_count = data['female_count'] or 0

    genders = ['Male', 'Female']
    borrow_counts = [male_count, female_count]

    return genders, borrow_counts


def top_readers_for_author(author_id):
    return Reader.objects.filter(
        borrowhistory__book__authors__id=author_id
    ).annotate(
        total_books_by_author=Count('borrowhistory__book', distinct=True)
    ).order_by('-total_books_by_author')


def get_reader_ranking_by_category(category_id):

    return Reader.objects.filter(
        borrowhistory__book__bookbycategory__category_id=category_id
    ).annotate(
        total_borrows=Count('borrowhistory__book', distinct=True),
        avg_borrows=ExpressionWrapper(
            F('total_borrows') / Count('borrowhistory__book__bookbycategory__category', distinct=True),
            output_field=FloatField()
        )
    ).order_by('-avg_borrows')
        

def get_average_borrows_per_reader_in_library():

    return Library.objects.annotate(
        total_readers=Count('librarymember__reader', distinct=True),
        total_borrows=Count('librarymember__reader__borrowhistory', distinct=True),
        avg_borrows_per_reader=Case(
            When(total_readers=0, then=0),
            default=Avg('librarymember__reader__borrowhistory'),
            output_field=FloatField(),
        )
    ).filter(total_borrows__gt=0).order_by('-avg_borrows_per_reader')





def execute_queries_parallel():
    start_time = time.time()
    num_threads = 8
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {
            executor.submit(get_monthly_borrow_trends_by_category): 'monthly_borrow_trends',
            executor.submit(reader_activity_duration): 'reader_activity_duration',
            executor.submit(get_borrow_counts_by_gender): 'borrow_counts_by_gender',
            executor.submit(top_readers_for_author, author_id=1): 'top_readers_for_author', 
            executor.submit(get_reader_ranking_by_category, category_id=1): 'reader_ranking_by_category', 
            executor.submit(get_average_borrows_per_reader_in_library): 'average_borrows_per_reader_in_library',
        }

        results = {}
        for future in concurrent.futures.as_completed(futures):
            query_name = futures[future]
            try:
                result = future.result()
                if query_name == 'monthly_borrow_trends':
                    categories, months, borrow_counts = result
                    monthly_borrow_trends = zip(categories, months, borrow_counts)
                    results[query_name] = monthly_borrow_trends
                elif query_name == 'reader_activity_duration':
                    reader_names, durations = result
                    results[query_name] = zip(reader_names, durations)
                else:
                    results[query_name] = result
            except Exception as e:
                results[query_name] = f"Error: {e}"

    end_time = time.time()
    execution_time = end_time - start_time 

    results['execution_time'] = execution_time
    results['num_threads'] = num_threads

    return results


def run_experiment(thread_count):
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(get_monthly_borrow_trends_by_category) for _ in range(200)]

        results = [future.result() for future in futures]

    end_time = time.time()
    execution_time = end_time - start_time

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    return execution_time, cpu_usage, memory_usage, results

def measure_execution_time(thread_count):
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        results = list(executor.map(lambda _: reader_activity_duration(), range(thread_count)))

    execution_time = time.time() - start_time
    return execution_time

def perform_experiments():
    thread_counts = [1, 2, 4, 8, 16, 32]  
    execution_times = []  
    
    for threads in thread_counts:
        execution_time = measure_execution_time(threads)
        execution_times.append(execution_time)
    
    return thread_counts, execution_times

def generate_execution_time_graph(thread_counts, execution_times):
   
    trace = go.Scatter(
        x=thread_counts, 
        y=execution_times, 
        mode='lines+markers',
        name='Час виконання'
    )
    
    layout = go.Layout(
        title='Залежність часу виконання від кількості потоків',
        xaxis=dict(title='Кількість потоків'),
        yaxis=dict(title='Час виконання (сек.)')
    )
    
    figure = go.Figure(data=[trace], layout=layout)
    graph_html = figure.to_html(full_html=False)
    
    return graph_html

