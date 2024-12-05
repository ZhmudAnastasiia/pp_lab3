from rest_framework import serializers
from .models import Library, Author, Book, Reader, BorrowHistory

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class ReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = '__all__'

class BorrowHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowHistory
        fields = '__all__'
        

class MonthlyBorrowTrendsByCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    month = serializers.DateField()
    borrow_count = serializers.IntegerField()

class ReaderActivityDurationSerializer(serializers.Serializer):
    reader_id = serializers.IntegerField()
    activity_duration = serializers.DurationField()

class BorrowsCountByGenderSerializer(serializers.Serializer):
    male_borrows = serializers.IntegerField()
    female_borrows = serializers.IntegerField()

class TopReadersForAuthorSerializer(serializers.Serializer):
    reader_id = serializers.IntegerField(source='id')  # Вказуємо на поле id
    total_books_by_author = serializers.IntegerField()

class ReaderRankingByCategorySerializer(serializers.Serializer):
    reader_id = serializers.IntegerField(source='id')
    total_borrows = serializers.IntegerField()
    avg_borrows = serializers.FloatField()

class AverageBorrowsPerReaderInLibrarySerializer(serializers.Serializer):
    library_id = serializers.IntegerField(source='id')
    avg_borrows_per_reader = serializers.FloatField()




    