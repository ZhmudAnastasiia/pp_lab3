from .models_repo import LibraryRepo, ReaderRepo, BookRepo, AuthorRepo, BorrowHistoryRepo
 
def __init__(self):
        self.libraries = LibraryRepo()
        self.readers = ReaderRepo()
        self.books = BookRepo()
        self.authors = AuthorRepo()
        self.borrow_histories = BorrowHistoryRepo()