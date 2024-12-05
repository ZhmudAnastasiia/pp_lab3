from .base_repo import BaseRepo
from main.models import Library, Reader, Book, Author, BorrowHistory

class LibraryRepo(BaseRepo):
    def __init__(self):
        super().__init__(Library)

    def get_by_name(self, name):
        return self.model.objects.filter(name__icontains=name)

class ReaderRepo(BaseRepo):
    def __init__(self):
        super().__init__(Reader)

    def get_by_phone(self, phone):
        return self.model.objects.filter(phone_number=phone).first()

    def get_readers_in_city(self, city):
        return self.model.objects.filter(city__icontains=city)

class BookRepo(BaseRepo):
    def __init__(self):
        super().__init__(Book)

    def get_by_title(self, title):
        return self.model.objects.filter(title__icontains=title)

    def get_books_by_author(self, author_id):
        return self.model.objects.filter(authors__id=author_id)

    def get_books_by_category(self, category_id):
        return self.model.objects.filter(categories__id=category_id)

class AuthorRepo(BaseRepo):
    def __init__(self):
        super().__init__(Author)

    def get_by_full_name(self, first_name, last_name):
        return self.model.objects.filter(first_name=first_name, last_name=last_name).first()


class BorrowHistoryRepo(BaseRepo):
    def __init__(self):
        super().__init__(BorrowHistory)

    def get_history_by_reader(self, reader_id):
        return self.model.objects.filter(reader_id=reader_id)

    def get_borrowed_books(self, reader_id):
        return self.model.objects.filter(reader_id=reader_id).select_related('book')

