from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .forms import BookForm, CollectionForm, BorrowRequestForm, BorrowerReviewForm, CollectionAccessRequestForm, BookReviewForm
from .models import Book, Collection, BorrowRequest, BorrowerReview, CollectionAccessRequest
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.shortcuts import render
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
import logging

from .forms import *
from .models import *

logger = logging.getLogger(__name__)


@login_required
def provide_book_view(request):
    if request.user.role != 'provider':
        messages.error(request, "Access Denied: You must be an approved provider to access this page.")
        return redirect('choose')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            messages.success(request, "Book submitted successfully!")
            return redirect('provide_page')
        else:
            messages.error(request, "There was an error submitting your book.")
    else:
        form = BookForm()

    logger.debug("DEBUG: form fields = %s", list(form.fields.keys()))
    return render(request, 'accounts/provide.html', {'form': form})


def borrow_books_view(request):
    query = request.GET.get('q', '').strip()

    private_collections = Collection.objects.filter(visibility='private')
    # get all UUIDs of books in private collections
    private_uuids = (
        Book.objects
            .filter(collection__in=private_collections)
            .values_list('uuid', flat=True)
    )
    # exclude them
    books = Book.objects.exclude(uuid__in=private_uuids)
    books = books.annotate(avg_rating=Avg('review__rating'))
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        )

    books = books.order_by('-created_at')

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/borrow.html', {
        'page_obj': page_obj,
        'query': query
    })

@login_required
def create_collection_view(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user
            collection.save()
            form.save_m2m()

            if collection.visibility == 'private':
                collection.allowed_users.add(request.user)

            if not collection.books.exists():
                messages.error(request, "A collection must contain at least one book.")
                collection.delete()
                return redirect('create_collection_page')

            if (collection.visibility == 'private' and
                request.user.role == 'borrower'):
                messages.error(request, "Patrons cannot create private collections.")
                collection.delete()
                return redirect('create_collection_page')

            # enforce cross-collection constraints...
            for book in collection.books.all():
                other = book.collection_set.exclude(id=collection.id)
                if collection.visibility == 'private' and other.exists():
                    messages.error(
                        request,
                        f"Book '{book.title}' cannot join private if in other collections."
                    )
                    collection.delete()
                    return redirect('create_collection_page')
                if (collection.visibility == 'public' and
                    other.filter(visibility='private').exists()):
                    messages.error(
                        request,
                        f"Book '{book.title}' already in private, can't make public."
                    )
                    collection.delete()
                    return redirect('create_collection_page')

            messages.success(request, "Collection created successfully!")
            return redirect('choose')
        else:
            messages.error(request, "There was an error with your form.")
    else:
        form = CollectionForm()

    return render(request, 'books/create_collection.html', {'form': form})


def list_collection_view(request):
    collections = Collection.objects.all()
    for c in collections:
        c.can_access = c.visibility == 'public' or request.user in c.allowed_users.all()
    return render(request, 'books/collection_list.html', {'collections': collections})


@login_required
def collection_detail_view(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    books_in_collection = Book.objects.filter(collection=collection)

    if collection.visibility == 'public' or request.user in collection.allowed_users.all():
        return render(request, 'books/collection_detail.html', {
            'collection': collection,
            'books': books_in_collection,
        })

    messages.error(request, "You do not have access to this private collection.")
    return redirect('list_collection_page')


@login_required
def edit_collection_view(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if collection.creator != request.user:
        messages.error(request, "No permission to edit this collection.")
        return redirect('books/collection_detail', pk=collection.pk)

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            updated = form.save()
            if updated.visibility == 'private':
                updated.allowed_users.add(updated.creator)
            messages.success(request, "Collection updated successfully!")
            return redirect('collection_detail', pk=collection.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CollectionForm(instance=collection)

    return render(request, 'books/edit_collection.html', {
        'form': form,
        'collection': collection
    })


@login_required
def delete_collection_view(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if collection.creator != request.user:
        messages.error(request, "No permission to delete.")
        return redirect('books/collection_detail', pk=collection.pk)

    if request.method == 'POST':
        collection.delete()
        messages.success(request, "Collection deleted successfully!")
        return redirect('choose')

    return render(request, 'books/delete_collection.html', {
        'collection': collection
    })

@login_required
def collection_access_request_view(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        form = CollectionAccessRequestForm(request.POST)
        if form.is_valid():
            access_request = form.save(commit=False)
            access_request.collection = collection
            access_request.requester = request.user
            access_request.save()
            messages.success(request, "Access request submitted successfully!")
            return redirect('list_collection_page')
        else:
            messages.error(request, "There was an error with your request.")
    else:
        form = CollectionAccessRequestForm()

    return render(request, 'books/collection_access_request.html', {'form': form, 'collection': collection})

@login_required
def book_detail(request, book_uuid):
    book = get_object_or_404(Book, uuid=book_uuid)
    return render(request, 'books/detail.html', {'book': book})


@login_required
def request_borrow_book(request, book_uuid):
    book = get_object_or_404(Book, uuid=book_uuid)

    private_collections = book.collection_set.filter(visibility='private')

    if private_collections.exists():
        if not private_collections.filter(allowed_users=request.user).exists():
            messages.error(request, "You do not have access to borrow this book-it's in a private collection.")
            return redirect('borrow_page')

    if book.current_borrower:
        messages.error(request, f"'{book.title}' is already borrowed.")
        return redirect('book_detail', book_uuid=book.uuid)

    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.requester = request.user
            br.book = book
            br.save()
            messages.success(request, "Borrow request submitted!")
            return redirect('book_detail', book_uuid=book.uuid)
    else:
        form = BorrowRequestForm()

    return render(request, 'books/borrow_request_form.html', {
        'form': form,
        'book': book
    })


@login_required
def review_borrower(request, request_id):
    br = get_object_or_404(
        BorrowRequest,
        pk=request_id,
        status='returned',
        book__user=request.user
    )
    if hasattr(br, 'review'):
        return redirect('list_borrow_request_page')

    if request.method == 'POST':
        form = BorrowerReviewForm(request.POST)
        if form.is_valid():
            BorrowerReview.objects.create(
                borrow_request=br,
                reviewer=request.user,
                borrower=br.requester,
                rating=form.cleaned_data['rating']
            )
            messages.success(request, "Review submitted successfully!")
            return redirect('list_borrow_request_page')
    else:
        form = BorrowerReviewForm()

    return render(request, 'books/review_form.html', {
        'form': form,
        'br': br
    })


@login_required
def list_my_borrow_request_view(request):
    brs = BorrowRequest.objects.filter(requester=request.user).order_by('-id')
    
    returned_requests = BorrowRequest.objects.all().filter(
        status='returned',
        requester=request.user,
        book_review__isnull=True
    ).order_by('-approved_at')

    approved_requests = BorrowRequest.objects.all().filter(
        status='approved',
        requester=request.user,
    ).order_by('-approved_at')

    rejected_requests = BorrowRequest.objects.all().filter(
        status='rejected',
        requester=request.user,
    ).order_by('-approved_at')

    pending_requests = BorrowRequest.objects.all().filter(
        status='pending',
        requester=request.user,
    ).order_by('-approved_at')

    return render(request, 'books/my_borrow_request_list.html', {
        
        'borrow_requests': brs,
        'returned_requests': returned_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'pending_requests': pending_requests
})


@login_required
def list_borrow_request_view(request):
    borrow_requests = BorrowRequest.objects.all().order_by('-id')

    pending_requests = BorrowRequest.objects.all().filter(
        status='pending',
        book__user=request.user,
    ).order_by('-approved_at')

    approved_requests = BorrowRequest.objects.all().filter(
        status='approved',
        book__user=request.user,
    ).order_by('-approved_at')

    return render(request, 'books/borrow_request_list.html', {
        'borrow_requests': borrow_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests
    })

@login_required
def list_my_collection_request_view(request):
    collection_requests = CollectionAccessRequest.objects.filter(requester = request.user).order_by('-id')

    pending_requests = CollectionAccessRequest.objects.all().filter(
        status='pending',
        requester=request.user,
    ).order_by('-id')

    approved_requests = CollectionAccessRequest.objects.all().filter(
        status='approved',
        requester=request.user,
    ).order_by('-id')

    rejected_requests = CollectionAccessRequest.objects.all().filter(
        status='rejected',
        requester=request.user,
    ).order_by('-id')

    return render(request, 'books/my_collection_request_list.html', {
        'collection_requests': collection_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests
    })


@login_required
def list_collection_request_view(request):
    collection_requests = CollectionAccessRequest.objects.all().order_by('-id')

    pending_requests = CollectionAccessRequest.objects.all().filter(
        status='pending',
        collection__creator=request.user,
    ).order_by('-id')

    return render(request, 'books/collection_request_list.html', {
        'collection_requests': collection_requests,
        'pending_requests': pending_requests
    })

@login_required
def handle_borrow_request_view(request, request_id, action):
    br = get_object_or_404(BorrowRequest, pk=request_id)

    if request.user.role != 'provider':
        messages.error(request, "You don't have permission.")
        return redirect('choose')

    if action == 'accept':
        if br.book.current_borrower is None:
            br.status = 'approved'
            br.responded_by = request.user
            br.approved_at = timezone.now()
            br.book.current_borrower = br.requester
            br.book.save()
            messages.success(request, "Request accepted.")
        else:
            messages.error(request, "Already borrowed by someone else.")

    elif action == 'decline':
        br.status = 'rejected'
        br.responded_by = request.user
        br.approved_at = timezone.now()
        messages.success(request, "Request declined.")

    elif action == 'returned':
        if br.status != 'approved':
            messages.warning(request, "Only approved requests can be returned.")
        else:
            br.status = 'returned'
            br.book.current_borrower = None
            br.book.save()
            br.save()
            messages.success(request, "Marked as returned.")
            return redirect('borrower_review', request_id=br.id)

    else:
        messages.error(request, "Invalid action.")

    br.save()
    return redirect('book_detail', book_uuid=br.book.uuid)

    br.save()
    return redirect('book_detail', book_id=br.book.id) 

@login_required
def handle_collection_access_request_view(request, request_id, action):
    collection_request = get_object_or_404(CollectionAccessRequest, pk=request_id)

    if not request.user == collection_request.collection.creator:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('choose')
    
    if action == 'accept':
        collection_request.status = 'approved'
        collection_request.responded_by = request.user
        collection_request.approved_at = timezone.now()
        collection_request.collection.allowed_users.add(collection_request.requester)
        messages.success(request, "Collection access request accepted.")
    elif action == 'decline':
        collection_request.status = 'rejected'
        collection_request.responded_by = request.user
        collection_request.approved_at = timezone.now()
        messages.success(request, "Collection access request declined.")
    else:
        messages.error(request, "Invalid action.")
        return redirect('choose')
    
    collection_request.save()
    return redirect('list_collection_request_page')


@login_required
def my_books_view(request):
    if not request.user.is_provider_approved:
        messages.error(request, "Access Denied: You must be provider-approved.")
        return redirect('choose')

    books = Book.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'books/my_books.html', {'books': books})


@login_required
def delete_book_view(request, book_uuid):
    book = get_object_or_404(Book, uuid=book_uuid, user=request.user)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted successfully.")
        return redirect('my_books')

    return render(request, 'books/confirm_delete.html', {'book': book})


@login_required
def list_my_collections_view(request):
    cols = Collection.objects.filter(creator=request.user).order_by('-id')
    return render(request, 'books/my_collections.html', {
        'collections': cols
    })

def review_book_view(request, request_id):
    borrow_request = get_object_or_404(
        BorrowRequest,
        id = request_id,
        status = 'returned',
        requester=request.user,
        book_review__isnull=True
    )

    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit = False)
            review.borrow_request = borrow_request
            review.reviewer = request.user
            review.book = borrow_request.book
            review.save()
            messages.success(request, "Book review submitted!")
            return redirect('list_my_borrow_request_page')
    else:
        form = BookReviewForm()
        
    return render (request, 'books/book_review_form.html', {
        'form': form,
        'book': borrow_request.book
    })

def book_reviews_list(request, book_uuid):
    prev = request.META.get('HTTP_REFERER', reverse('choose'))
    book = get_object_or_404(Book, uuid = book_uuid)
    reviews = BookReview.objects.filter(book=book).order_by('-created_at')
    return render(request, 'books/book_reviews_list.html', {
        'book': book,
        'reviews': reviews,
        'prev_url': prev,
    })