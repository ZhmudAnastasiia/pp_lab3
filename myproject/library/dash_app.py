import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from .aggregated_queries import (
    monthly_borrow_trends_by_category,
    reader_activity_duration,
    borrows_count_by_gender,
    top_readers_for_author,
    reader_ranking_by_category,
    average_borrows_per_reader_in_library
)

# Ініціалізація Dash-додатку
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Інтерактивний дашборд для аналітичних даних бібліотеки"),

    # Додати елементи управління (слайдери, спадні списки)
    html.Label("Фільтр за категорією:"),
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Категорія 1', 'value': 1},
            {'label': 'Категорія 2', 'value': 2},
            {'label': 'Категорія 3', 'value': 3},
        ],
        value=1  # за замовчуванням
    ),

    # Графіки
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2'),
    dcc.Graph(id='graph3'),
    dcc.Graph(id='graph4'),
    dcc.Graph(id='graph5'),
    dcc.Graph(id='graph6'),
])

@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure'),
     Output('graph5', 'figure'),
     Output('graph6', 'figure')],
    [Input('category-dropdown', 'value')]
)
def update_graphs(category_id):
    # Виконання запитів для отримання даних
    trends_data = monthly_borrow_trends_by_category()
    trend_categories = [data['name'] for data in trends_data]
    trend_months = [data['month'].strftime('%Y-%m') for data in trends_data]
    borrow_count = [data['borrow_count'] for data in trends_data]

    graph1 = {
        'data': [go.Bar(x=trend_months, y=borrow_count, text=trend_categories)],
        'layout': go.Layout(
            title='Тренди позичених книг по категоріях за місяцями',
            xaxis={'title': 'Місяць'},
            yaxis={'title': 'Кількість позичених книг'}
        )
    }

    reader_activity = reader_activity_duration()
    readers = [reader.name for reader in reader_activity]
    activity_duration = [reader.activity_duration.total_seconds() / (60 * 60) for reader in reader_activity]

    graph2 = {
        'data': [go.Bar(x=readers, y=activity_duration)],
        'layout': go.Layout(
            title='Активність читачів за тривалістю використання бібліотеки (години)',
            xaxis={'title': 'Читач'},
            yaxis={'title': 'Тривалість активності (години)'}
        )
    }

    gender_borrows = borrows_count_by_gender()
    male_borrows = [gender_borrows[0].male_borrows]
    female_borrows = [gender_borrows[0].female_borrows]

    graph3 = {
        'data': [go.Pie(labels=['Чоловіки', 'Жінки'], values=[male_borrows[0], female_borrows[0]])],
        'layout': go.Layout(
            title='Кількість позичених книг за статтю'
        )
    }

    top_readers = top_readers_for_author(author_id=1)  # Замініть на ID автора
    reader_names = [reader.name for reader in top_readers]
    total_books = [reader.total_books_by_author for reader in top_readers]

    graph4 = {
        'data': [go.Bar(x=reader_names, y=total_books)],
        'layout': go.Layout(
            title='Топ-читачі за кількістю позичених книг від автора',
            xaxis={'title': 'Читач'},
            yaxis={'title': 'Кількість книг'}
        )
    }

    category_ranking = reader_ranking_by_category(category_id=category_id)  # Динамічне оновлення
    reader_names_ranking = [reader.name for reader in category_ranking]
    avg_borrows = [reader.avg_borrows for reader in category_ranking]

    graph5 = {
        'data': [go.Bar(x=reader_names_ranking, y=avg_borrows)],
        'layout': go.Layout(
            title='Рейтинг читачів по категоріям',
            xaxis={'title': 'Читач'},
            yaxis={'title': 'Середня кількість позичених книг'}
        )
    }

    avg_borrows_per_lib = average_borrows_per_reader_in_library()
    library_names = [library.name for library in avg_borrows_per_lib]
    avg_borrows_per_reader = [library.avg_borrows_per_reader for library in avg_borrows_per_lib]

    graph6 = {
        'data': [go.Bar(x=library_names, y=avg_borrows_per_reader)],
        'layout': go.Layout(
            title='Середня кількість позичених книг на читача в бібліотеці',
            xaxis={'title': 'Бібліотека'},
            yaxis={'title': 'Середня кількість позичених книг'}
        )
    }

    return graph1, graph2, graph3, graph4, graph5, graph6

