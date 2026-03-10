from django.contrib import admin
from .models import Book, Collection, BorrowRequest, BorrowerReview
# Register your models here.

admin.site.register(Book)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility', 'creator')  # Optional, for overview
    filter_horizontal = ('books', 'allowed_users') 

admin.site.register(BorrowRequest)
admin.site.register(BorrowerReview)