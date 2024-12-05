import os
import sys
import pandas as pd
from django.db.models import Avg, Min, Max, Count
sys.path.append('D:/lab3_zhmud/myproject')  # Додайте шлях до вашого проекту
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
import django
django.setup()

# Імпортуємо необхідні моделі
from library.models import BorrowHistory, Book, BookCategory, BookByCategory

# Функція для обчислення статистики через Django ORM
def get_statistics_orm():
    # Обчислити середнє, мінімум, максимум для borrow_date та return_date
    stats_borrow = BorrowHistory.objects.aggregate(
        avg_borrow_date=Avg('borrow_date'),
        min_borrow_date=Min('borrow_date'),
        max_borrow_date=Max('borrow_date')
    )
    stats_return = BorrowHistory.objects.aggregate(
        avg_return_date=Avg('return_date'),
        min_return_date=Min('return_date'),
        max_return_date=Max('return_date')
    )

    print(f"Statistics for Borrow Date (ORM):")
    print(f"Average Borrow Date: {stats_borrow['avg_borrow_date']}")  # Це виведе середню дату
    print(f"Min Borrow Date: {stats_borrow['min_borrow_date']}")
    print(f"Max Borrow Date: {stats_borrow['max_borrow_date']}")
    
    print(f"\nStatistics for Return Date (ORM):")
    print(f"Average Return Date: {stats_return['avg_return_date']}")
    print(f"Min Return Date: {stats_return['min_return_date']}")
    print(f"Max Return Date: {stats_return['max_return_date']}")

    # Групування за категорією книги та обчислення середнього публікаційного року
    category_stats = Book.objects.values('categories__name').annotate(
        avg_publication_year=Avg('publication_year'),
        min_publication_year=Min('publication_year'),
        max_publication_year=Max('publication_year')
    )
    
    print(f"\nStatistics by Category (ORM):")
    for stat in category_stats:
        print(f"Category: {stat['categories__name']}")
        print(f"Average Publication Year: {stat['avg_publication_year']}")
        print(f"Min Publication Year: {stat['min_publication_year']}")
        print(f"Max Publication Year: {stat['max_publication_year']}")

# Функція для обчислення статистики через pandas
def get_statistics_pandas():
    # Завантажуємо дані для BorrowHistory, включаючи книги та категорії
    borrow_history = BorrowHistory.objects.all().select_related('book').prefetch_related('book__categories').values('borrow_date', 'return_date', 'book__title', 'book__publication_year', 'book__categories__name')

    if borrow_history:
        # Створюємо DataFrame з отриманих даних
        df = pd.DataFrame(borrow_history)

        # Перевірка чи є дані для обчислень
        if not df.empty:
            # Обчислюємо статистику для borrow_date та return_date
            avg_borrow_date = df['borrow_date'].mean()
            min_borrow_date = df['borrow_date'].min()
            max_borrow_date = df['borrow_date'].max()
            median_borrow_date = df['borrow_date'].median()

            print(f"\nStatistics for Borrow Date (Pandas):")
            print(f"Average Borrow Date: {avg_borrow_date}")
            print(f"Min Borrow Date: {min_borrow_date}")
            print(f"Max Borrow Date: {max_borrow_date}")
            print(f"Median Borrow Date: {median_borrow_date}")

            # Статистика по категоріях
            df_categories = df['book__categories__name']
            category_counts = df_categories.value_counts()

            print(f"\nCategory Counts (Pandas):")
            print(category_counts)

            # Групування за публікаційним роком та категоріями
            publication_year_group = df.groupby('book__publication_year').agg(
                avg_borrow_date=('borrow_date', 'mean'),
                min_borrow_date=('borrow_date', 'min'),
                max_borrow_date=('borrow_date', 'max')
            )

            print(f"\nStatistics by Publication Year (Pandas):")
            print(publication_year_group)

            # Групування за місяцем позики
            df['borrow_month'] = df['borrow_date'].dt.month
            month_group = df.groupby('borrow_month').agg(
                avg_borrow_date=('borrow_date', 'mean'),
                min_borrow_date=('borrow_date', 'min'),
                max_borrow_date=('borrow_date', 'max')
            )

            print(f"\nStatistics by Borrow Month (Pandas):")
            print(month_group)
        else:
            print("No data found for BorrowHistory or Book.")
    else:
        print("No BorrowHistory records found.")

# Запуск аналізу
if __name__ == "__main__":
    print("Django ORM Statistics:")
    get_statistics_orm()

    print("\nPandas Statistics:")
    get_statistics_pandas()
