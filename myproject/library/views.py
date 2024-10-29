from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Library, Author, Book, Reader, BorrowHistory
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
