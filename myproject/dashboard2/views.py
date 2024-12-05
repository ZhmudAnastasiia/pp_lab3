from django.shortcuts import render
from library.queries import get_monthly_borrow_trends_by_category,reader_activity_duration, get_borrow_counts_by_gender, top_readers_for_author, get_average_borrows_per_reader_in_library,get_reader_ranking_by_category
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.embed import components
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, Slider, CustomJS
from bokeh.layouts import column
from bokeh.models.widgets import Select
from django.http import HttpResponse
from collections import defaultdict
from itertools import cycle
from bokeh.palettes import Category10
from bokeh.palettes import Viridis256
from bokeh.models import FactorRange


def plot_borrow_trends(month_filter=None):
    categories, months, borrow_counts = get_monthly_borrow_trends_by_category()
    aggregated_data = defaultdict(int)
    for month, count in zip(months, borrow_counts):
        aggregated_data[month] += count

    aggregated_months = list(aggregated_data.keys())
    aggregated_borrow_counts = list(aggregated_data.values())
    
    if month_filter:
        filtered_months = [month for month in aggregated_months if month == month_filter]
        filtered_borrow_counts = [aggregated_borrow_counts[i] for i, month in enumerate(aggregated_months) if month == month_filter]
    else:
        filtered_months = aggregated_months
        filtered_borrow_counts = aggregated_borrow_counts

    p = figure(x_range=FactorRange(*filtered_months), height=350, title="Monthly Borrow Trends by Category", toolbar_location=None)
    p.vbar(x=filtered_months, top=filtered_borrow_counts, width=0.9, color=Category10[10][0])

    return p


def borrow_trends_view(request):
    month_filter = request.GET.get('month', None)

    print("Month Filter:", month_filter)

    plot = plot_borrow_trends(month_filter)
    script, div = components(plot)

    return render(request, 'library/monthly_borrow_trends_b.html', {
        'script': script,
        'div': div
    })

def plot_reader_activity(reader_names, durations):
    source = ColumnDataSource(data={
        "reader_names": reader_names,
        "durations": durations
    })

    p = figure(
        y_range=reader_names,
        x_axis_label="Activity Duration (days)",
        y_axis_label="Readers",
        title="Reader Activity Duration",
        height=600,
        width=800,
        tools="pan,box_zoom,reset,save"
    )
    p.hbar(
        y="reader_names",
        right="durations",
        height=0.5,
        source=source,
        color="navy",
        alpha=0.7
    )

    return p, source

def reader_activity_view(request):
    reader_names, durations = reader_activity_duration()
    plot, source = plot_reader_activity(reader_names, durations)

    slider = Slider(start=0, end=max(durations) if durations else 0, value=max(durations), step=1, title="Max Duration")

    slider.js_on_change("value", CustomJS(args=dict(source=source), code="""
        const data = source.data;
        const max_duration = cb_obj.value;
        const new_durations = data['durations'].map(val => val > max_duration ? max_duration : val);
        data['durations'] = new_durations;
        source.change.emit();
    """))

    layout = column(plot, slider)

    script, div = components(layout)

    return render(request, 'library/reader_activity.html', {
        'script': script,
        'div': div
    })


def create_simple_bar_chart(genders, borrow_counts):
    if not genders or not borrow_counts:
        print("Empty data: genders or borrow_counts.")
        return None

    if len(genders) != len(borrow_counts):
        print("Error: Mismatched lengths between genders and borrow_counts.")
        return None

    data = pd.DataFrame({
        'genders': genders,
        'borrow_counts': borrow_counts
    })

    color_cycle = cycle(Viridis256)

    data['colors'] = [next(color_cycle) for _ in range(len(borrow_counts))]

    source = ColumnDataSource(data)

    p = figure(x_range=genders, height=350, title="Borrow Counts by Gender", toolbar_location=None, tools="hover",
               tooltips="@genders: @borrow_counts", x_axis_label='Gender', y_axis_label='Borrow Count')

    p.vbar(x='genders', top='borrow_counts', width=0.9, source=source, legend_field='genders', fill_color='colors')

    p.legend.title = "Genders"
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0.3

    return p, source

def pie_chart_view(request):
    genders, borrow_counts = get_borrow_counts_by_gender()

    plot, source = create_simple_bar_chart(genders, borrow_counts)

    if plot is None:
        print("Error creating pie chart.")
        return HttpResponse("Error generating pie chart.")

    select = Select(title="Select Gender:", value="All", options=["All"] + genders)

    select.js_on_change("value", CustomJS(args=dict(source=source, genders=genders, borrow_counts=borrow_counts), code="""
    const data = source.data;
    const selected_gender = cb_obj.value;
    
    // Визначаємо індекси для кожного гендеру
    const genderIndex = {
        'Male': 0,
        'Female': 1,
        'Other': 2
    };

    // Якщо вибрано "All", відображаємо всі значення
    if (selected_gender === 'All') {
        data['borrow_counts'] = borrow_counts;
        data['colors'] = data['genders'].map((gender, idx) => {
            return genderIndex[gender] === 0 ? '#1f77b4' : (genderIndex[gender] === 1 ? '#ff7f0e' : '#2ca02c');
        });
    } else {
        // Встановлюємо 0 для інших гендерів, щоб приховати їх
        let newBorrowCounts = [0, 0, 0];
        newBorrowCounts[genderIndex[selected_gender]] = borrow_counts[genderIndex[selected_gender]];

        data['borrow_counts'] = newBorrowCounts;
        data['colors'] = newBorrowCounts.map(count => count > 0 ? (count === borrow_counts[0] ? '#1f77b4' : (count === borrow_counts[1] ? '#ff7f0e' : '#2ca02c')) : '#ffffff');
    }

    source.change.emit();  // Оновлюємо дані на графіку
    """))

    layout = column(select, plot)

    script, div = components(layout)

    return render(request, 'library/borrow_counts_by_gender.html', {
        'script': script,
        'div': div
    })




def create_top_readers_pie_chart(readers, borrow_counts):
    if not readers or not borrow_counts:
        print("Empty data: readers or borrow_counts.")
        return None

    if len(readers) != len(borrow_counts):
        print("Error: Mismatched lengths between readers and borrow_counts.")
        return None

    data = pd.DataFrame({
        'readers': readers,
        'borrow_counts': borrow_counts
    })

    data['angle'] = data['borrow_counts'] / data['borrow_counts'].sum() * 2 * np.pi

    color_cycle = cycle(Viridis256)
    colors = [next(color_cycle) for _ in range(len(borrow_counts))]

    data['color'] = colors

    source = ColumnDataSource(data)

    p = figure(title="Top Readers for Author", toolbar_location=None, tools="hover", tooltips="@readers: @borrow_counts", x_range=(-1, 1), y_range=(-1, 1))

    p.wedge(x=0, y=0, radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='readers', source=source)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    p.legend.title = "Readers"
    p.legend.location = "top_left"

    return p, source

def top_readers_view(request, author_id):
    print("Received request for top readers view.")
    readers_data = top_readers_for_author(author_id)

    readers = [f"{reader.first_name} {reader.last_name}" for reader in readers_data]
    borrow_counts = [reader.total_books_by_author for reader in readers_data]

    plot, source = create_top_readers_pie_chart(readers, borrow_counts)

    if plot is None:
        print("Error creating chart.")
        return HttpResponse("Error generating chart.")
    slider = Slider(start=0, end=max(borrow_counts), value=0, step=1, title="Minimum Borrow Count")

    slider.js_on_change("value", CustomJS(args=dict(source=source), code="""
    const data = source.data;
    const min_borrow = cb_obj.value;
    
    let filtered_counts = [];
    let filtered_readers = [];
    let filtered_angles = [];
    let filtered_colors = [];

    // Перевірка кожного значення та фільтрація
    for (let i = 0; i < data['borrow_counts'].length; i++) {
        if (data['borrow_counts'][i] >= min_borrow) {
            filtered_counts.push(data['borrow_counts'][i]);
            filtered_readers.push(data['readers'][i]);
            filtered_angles.push(data['angle'][i]);
            filtered_colors.push(data['color'][i]);
        }
    }

    // Оновлення даних для джерела
    data['borrow_counts'] = filtered_counts;
    data['readers'] = filtered_readers;
    data['angle'] = filtered_angles;
    data['color'] = filtered_colors;
    
    source.change.emit();
"""));

    layout = column(slider, plot)

    script, div = components(layout)

    return render(request, 'library/top_readers_by_author.html', {
        'script': script,
        'div': div
    })


def create_reader_ranking_bar_chart(readers, avg_borrows):
    if not readers or not avg_borrows:
        print("Empty data: readers or avg_borrows.")
        return None

    if len(readers) != len(avg_borrows):
        print("Error: Mismatched lengths between readers and avg_borrows.")
        return None
    if not all(isinstance(x, str) for x in readers):
        print("Error: All reader names must be strings.")
        return None
    if not all(isinstance(x, (int, float)) for x in avg_borrows):
        print("Error: All borrow averages must be numeric.")
        return None

    data = pd.DataFrame({
        'readers': readers,
        'avg_borrows': avg_borrows
    })

    color_cycle = cycle(Viridis256)
    colors = [next(color_cycle) for _ in range(len(data))]

    data['colors'] = colors

    p = figure(x_range=data['readers'], height=350, title="Reader Ranking by Category", toolbar_location=None, tools="hover",
               tooltips="@readers: @avg_borrows", x_axis_label='Readers', y_axis_label='Average Borrows')

    p.vbar(x='readers', top='avg_borrows', width=0.9, source=ColumnDataSource(data), legend_field='readers',
           fill_color='colors')

    p.legend.title = "Readers"
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0.3

    return p


def reader_ranking_view(request, category_id):
    sort_order = request.GET.get('sort_order', 'asc')
    readers_data = get_reader_ranking_by_category(category_id)

    if sort_order == 'asc':
        readers_data = readers_data.order_by('avg_borrows')
    elif sort_order == 'desc':
        readers_data = readers_data.order_by('-avg_borrows')

    readers = [f"{reader.first_name} {reader.last_name}" for reader in readers_data]
    avg_borrows = [reader.avg_borrows for reader in readers_data]

    if not readers or not avg_borrows:
        print("Error: No data available.")
    else:
        print(f"Readers: {readers}")
        print(f"Avg Borrows: {avg_borrows}")

    plot = create_reader_ranking_bar_chart(readers, avg_borrows)

    if plot is None:
        return HttpResponse("Error generating chart.")

    script, div = components(plot)

    return render(request, 'library/reader_ranking_by_category.html', {
        'script': script,
        'div': div,
        'category_id': category_id,
        'sort_order': sort_order
    })


def create_average_borrows_line_chart(libraries, avg_borrows):
    if not libraries or not avg_borrows:
        print("Empty data: libraries or avg_borrows.")
        return None

    data = {
        'libraries': libraries,
        'avg_borrows': avg_borrows,
    }

    source = ColumnDataSource(data)

    p = figure(title="Average Borrows per Reader in Library", 
               x_axis_label='Library', y_axis_label='Average Borrows', 
               height=400, width=800,
               x_range=FactorRange(*libraries)) 

    p.line(x='libraries', y='avg_borrows', source=source, line_width=2, legend_label="Avg Borrows per Reader", color="blue")

    p.scatter(x='libraries', y='avg_borrows', source=source, size=6, color="blue", legend_label="Data Points")
    
    p.legend.location = "top_left"
    p.grid.grid_line_alpha = 0.3

    return p


def average_borrows_view(request):

    libraries_data = get_average_borrows_per_reader_in_library()

    libraries = [library.name for library in libraries_data]
    avg_borrows = [library.avg_borrows_per_reader for library in libraries_data]

    min_borrows = min(avg_borrows, default=0)
    max_borrows = max(avg_borrows, default=0)

    min_filter = float(request.GET.get('min_borrows', min_borrows))
    max_filter = float(request.GET.get('max_borrows', max_borrows))

    filtered_libraries_data = [
        library for library in libraries_data
        if min_filter <= library.avg_borrows_per_reader <= max_filter
    ]

    filtered_libraries = [library.name for library in filtered_libraries_data]
    filtered_avg_borrows = [library.avg_borrows_per_reader for library in filtered_libraries_data]

    plot = create_average_borrows_line_chart(filtered_libraries, filtered_avg_borrows)

    if plot is None:
        return HttpResponse("Error generating chart.")

    script, div = components(plot)

    return render(request, 'library/average_borrows_by_library.html', {
        'script': script,
        'div': div,
        'min_borrows': min_borrows,  
        'max_borrows': max_borrows,
        'current_min_filter': min_filter,
        'current_max_filter': max_filter,
    })


