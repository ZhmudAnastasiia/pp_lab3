from django.db import models

class Library(models.Model):
    name = models.CharField(max_length=255, null=False)
    address = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name

class Reader(models.Model):
    city = models.CharField(max_length=255, null=False)
    street = models.CharField(max_length=255, null=False)
    house_number = models.CharField(max_length=10, null=False)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    gender = models.CharField(max_length=10, null=False)
    phone_number = models.CharField(max_length=15, null=False)
    email = models.EmailField(null=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=255, null=False)
    publication_year = models.IntegerField(null=False)
    authors = models.ManyToManyField('Author', through='BookByAuthor')
    categories = models.ManyToManyField('BookCategory', through='BookByCategory')
    loan_status = models.ForeignKey('LoanStatus', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Author(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    birth_year = models.IntegerField(null=False)
    death_year = models.IntegerField(null=True)  # Це поле може бути пустим

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BookByAuthor(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

class BookCategory(models.Model):
    name = models.CharField(max_length=100, null=False)

class BookByCategory(models.Model):
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

class LibraryMember(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.reader} - {self.library}"

class BorrowHistory(models.Model):
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(null=False)
    return_date = models.DateField(null=True)  # Це поле може бути пустим

class LoanStatus(models.Model):
    status_name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.status_name
