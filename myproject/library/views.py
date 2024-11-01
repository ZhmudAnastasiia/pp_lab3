from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .NetworkHelper import NetworkHelper
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import BookForm
from .models import Library, Author, Book, Reader, BorrowHistory, BookCategory
from .serializer import LibrarySerializer, AuthorSerializer, BookSerializer, ReaderSerializer, BorrowHistorySerializer

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
    context_object_name = 'books'  # Назва контексту, що міститиме список книг

class BookDetail(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'  # Назва контексту для детальної інформації про книгу
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = self.object.authors.all()
        context['categories'] = self.object.categories.all()  # Отримуємо всі категорії
        return context
    
    def form_valid(self, form):
        book = form.save()
        authors = self.request.POST.getlist('authors')  # Отримання вибраних авторів
        book.authors.set(authors)  # Встановлення авторів
        categories = self.request.POST.getlist('categories')  # Отримання вибраних категорій
        book.categories.set(categories)  # Встановлення категорій
        return redirect('library:book_list')

class BookCreate(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def form_valid(self, form):
        book = form.save(commit=False)
        book.save()

        # Отримуємо авторів і категорії з POST запиту
        authors = self.request.POST.getlist('authors')
        categories = self.request.POST.getlist('categories')

        # Додаємо авторів і категорії до книги
        book.authors.set(authors)  # Додає авторів
        book.categories.set(categories)  # Додає категорії

        return redirect('library:book_list')

class BookUpdate(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:book_list')

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['authors'] = Author.objects.all()  # Всі автори
       context['categories'] = BookCategory.objects.all()  # Всі категорії
       context['selected_authors'] = self.object.authors.all()  # Вибрані автори для книги
       context['selected_categories'] = self.object.categories.all()  # Вибрані категорії для книги
       return context

    def form_valid(self, form):
        book = form.save()  # Зберігаємо об'єкт книги

        # Отримуємо авторів та категорії з POST-запиту
        authors = self.request.POST.getlist('authors')
        categories = self.request.POST.getlist('categories')

        # Очищаємо попередні зв'язки та зберігаємо нові
        book.authors.clear()
        book.authors.add(*[get_object_or_404(Author, id=author_id) for author_id in authors])

        book.categories.clear()
        book.categories.add(*[get_object_or_404(BookCategory, id=category_id) for category_id in categories])

        return redirect('library:book_detail', pk=book.id)
    
class BookDelete(DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:book_list')  # URL для перенаправлення після успішного видалення


class AuthorCreateView(CreateView):
    model = Author
    template_name = 'library/author_form.html'
    fields = ['first_name', 'last_name', 'birth_year', 'death_year']

    def form_valid(self, form):
        form.save()
        return redirect('library:book_list')
    
class CategoryCreateView(CreateView):
    model = BookCategory
    template_name = 'library/category_form.html'  # Створіть шаблон для категорії
    fields = ['name']  # Припустимо, що у вас є поле 'name' у BookCategory

    def form_valid(self, form):
        form.save()
        return redirect('library:book_list')  # Перенаправлення на список книг

def viewer_list(request):
    viewers = NetworkHelper.getlist('http://127.0.0.1:8001/api/viewers/')  # Змініть URL на ваш
    return render(request, 'library/helper.html', {'viewers': viewers})

def delete_viewer(request, id):
    url = f'http://127.0.0.1:8001/api/viewers/{id}/'  # Змініть URL на ваш
    NetworkHelper.delete(url)
    return redirect('library:viewer_list')  # Змініть на ваш URL для списку глядачів

