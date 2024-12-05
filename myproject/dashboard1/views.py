from django.shortcuts import render
from library.queries import get_monthly_borrow_trends_by_category, reader_activity_duration,  get_borrow_counts_by_gender,  top_readers_for_author,  get_average_borrows_per_reader_in_library,  get_reader_ranking_by_category
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

def borrows_count_by_gender(request):
    genders, borrow_counts = get_borrow_counts_by_gender()

    gender_filter = request.GET.get('gender', None)

    if gender_filter:
        selected_genders = gender_filter.split(',')
        filtered_data = [
            (gender, count)
            for gender, count in zip(genders, borrow_counts)
            if gender in selected_genders
        ]

        genders, borrow_counts = zip(*filtered_data) if filtered_data else ([], [])

    pie_fig = px.pie(
        names=genders,
        values=borrow_counts,
        title='Borrow Distribution by Gender'
    )
    pie_graph = pio.to_html(pie_fig, full_html=False)

    return render(request, 'library/borrows_by_gender.html', {
        'pie_graph': pie_graph
    })

def monthly_borrow_trends_by_category(request):

    categories, months, borrow_counts = get_monthly_borrow_trends_by_category()

    bar_fig = px.bar(
        x=months,
        y=borrow_counts,  
        color=categories, 
        title='Monthly Borrow Trends by Category',
        labels={'x': 'Month', 'y': 'Borrow Count'},  
        barmode='stack' 
    )


    bar_graph = pio.to_html(bar_fig, full_html=False)

    return render(request, 'library/monthly_borrow_trends_by_category.html', {
        'bar_graph': bar_graph
    })

def reader_activity_graph_view(request):
    reader_names, durations = reader_activity_duration()

    max_duration = request.GET.get('max_duration', None)

    if max_duration:
        max_duration = int(max_duration)
        filtered_data = [
            (name, duration) 
            for name, duration in zip(reader_names, durations) 
            if duration <= max_duration
        ]
        reader_names, durations = zip(*filtered_data) if filtered_data else ([], [])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=reader_names,
        y=durations,
        mode='lines+markers',
        name='Тривалість активності'
    ))

    fig.update_layout(
        title='Тривалість активності читачів',
        xaxis_title='Читачі',
        yaxis_title='Тривалість (дні)',
        xaxis=dict(tickangle=45),  
        showlegend=True
    )

    graph = fig.to_html(full_html=False)

    return render(request, 'library/reader_activity_graph.html', {'graph': graph})


def top_readers_graph_view(request, author_id):
    top_readers = top_readers_for_author(author_id)

    min_books_read = request.GET.get('min_books_read', None)

    if min_books_read:
        try:
            min_books_read = int(min_books_read)
            top_readers = [reader for reader in top_readers if reader.total_books_by_author >= min_books_read]
        except ValueError:
            pass

    reader_names = []
    books_read = []

    for reader in top_readers:
        full_name = f"{reader.first_name} {reader.last_name}"
        reader_names.append(full_name)
        books_read.append(reader.total_books_by_author)  

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=books_read,
        y=reader_names,
        orientation='h',  
        marker=dict(color='blue'),
        name='Книги'
    ))

    fig.update_layout(
        title=f'Топ читачів автора ID {author_id}',
        xaxis_title='Кількість прочитаних книг',
        yaxis_title='Читачі',
        yaxis=dict(autorange="reversed"), 
        showlegend=False
    )

    graph = fig.to_html(full_html=False)

    return render(request, 'library/top_readers_graph.html', {'graph': graph, 'author_id': author_id})



def reader_ranking_graph_view(request, category_id):

    ranking_data = get_reader_ranking_by_category(category_id)

    sort_order = request.GET.get('sort_order', 'asc')  

    if sort_order == 'desc':
        ranking_data = ranking_data.order_by('-avg_borrows')  
    else:
        ranking_data = ranking_data.order_by('avg_borrows')  

    reader_names = []
    avg_borrows = []

    for reader in ranking_data:
        full_name = f"{reader.first_name} {reader.last_name}"
        reader_names.append(full_name)
        avg_borrows.append(reader.avg_borrows)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=reader_names,
        y=avg_borrows,
        marker=dict(color='green'),
        name='Середня кількість позик'
    ))

    fig.update_layout(
        title=f'Рейтинг читачів за категорією ID {category_id}',
        xaxis_title='Читачі',
        yaxis_title='Середня кількість позик',
        xaxis=dict(tickangle=-45),
        showlegend=False
    )

    graph = fig.to_html(full_html=False)

    return render(request, 'library/reader_ranking_graph.html', {'graph': graph, 'category_id': category_id})


from library.models import Library  

def average_borrows_graph_view(request):
    library_data = get_average_borrows_per_reader_in_library()

    library_names = []
    avg_borrows = []

    for library in library_data:
        library_names.append(library.name)
        avg_borrows.append(library.avg_borrows_per_reader)

    if not library_names or not avg_borrows:
        return render(request, 'library/no_data.html')

    selected_library = request.GET.get('library', None) 

    if selected_library:
        filtered_data = [
            (name, borrows)
            for name, borrows in zip(library_names, avg_borrows)
            if name == selected_library
        ]
    else:
        filtered_data = zip(library_names, avg_borrows)

    filtered_library_names, filtered_avg_borrows = zip(*filtered_data) if filtered_data else ([], [])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_library_names, 
        y=filtered_avg_borrows,  
        marker=dict(color='blue'),  
        text=filtered_avg_borrows, 
        textposition='auto'
    ))

    fig.update_layout(
        title='Середня кількість позик на читача для кожної бібліотеки',
        xaxis_title='Бібліотека',
        yaxis_title='Середня кількість позик',
        showlegend=False
    )

    graph = fig.to_html(full_html=False)

    libraries = Library.objects.all()

    return render(request, 'library/average_borrows_graph.html', {
        'graph': graph,
        'libraries': libraries,
        'selected_library': selected_library,
    })
