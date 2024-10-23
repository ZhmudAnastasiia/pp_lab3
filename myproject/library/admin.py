from django.contrib import admin
from .models import Library, Reader, Book, Author, BookByAuthor, BookByCategory, BookCategory, LibraryMember, BorrowHistory, LoanStatus

class BookByAuthorInline(admin.TabularInline):
    model = BookByAuthor
    extra = 1

class BookByCategoryInline(admin.TabularInline):
    model = BookByCategory
    extra = 1

class LibraryMemberInline(admin.TabularInline):
    model = LibraryMember
    extra = 1

class BorrowHistoryAdmin(admin.ModelAdmin):
    list_display = ('reader', 'book', 'borrow_date', 'return_date')

class BookAdmin(admin.ModelAdmin):
    inlines = [BookByAuthorInline, BookByCategoryInline]
    list_display = ('title', 'publication_year', 'get_loan_status')

    def get_loan_status(self, obj):
        return obj.loan_status.status_name if obj.loan_status else 'Немає статусу'
    get_loan_status.short_description = 'Статус'

class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookByAuthorInline]

class LibraryAdmin(admin.ModelAdmin):
    inlines = [LibraryMemberInline]

class LoanStatusAdmin(admin.ModelAdmin):
    list_display = ('status_name',)

admin.site.register(Library, LibraryAdmin)
admin.site.register(Reader)
admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(BookCategory)
admin.site.register(LibraryMember)
admin.site.register(BorrowHistory, BorrowHistoryAdmin)
admin.site.register(LoanStatus, LoanStatusAdmin)

