from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserImageForm, ProfileForm
from books.forms import BookForm
from books.models import Book, Collection
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.db.models import Q
from books.models import Book
from django.db.models import Avg

CustomUser = get_user_model()

def home(request):
    return render(request, 'accounts/home.html')

def anonymous_view(request):
    return render(request, 'accounts/anonymous.html')

def lending_policies_view(request):
     return render(request, 'accounts/lending_policies.html')

@login_required
def choose_view(request):
    if request.method == 'POST':
        choice = request.POST.get('choice')  # 'provider' or 'borrower'
        
        if choice == 'provider':
            # Check if the user is approved
            if request.user.is_provider_approved:
                request.user.role = 'provider'
                request.user.save()
                return redirect('provide_page')
            else:
                messages.error(request, "You do not have permission to be a provider yet.")
                #return redirect('request_provider')  # Redirect to a view where they can request provider status.
        elif choice == 'borrower':
            # They want to be a borrower
            request.user.role = 'borrower'
            request.user.save()
            return redirect('borrow_page')

    return render(request, 'accounts/choose.html')

@login_required
def provide_view(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user  # Associate the book with the logged-in user
            book.save()
            messages.success(request, "Book submitted successfully!")
            return redirect('provide_page')  # Ensure this URL name matches your URL config
        else:
            messages.error(request, "There was an error submitting your book.")
    else:
        form = BookForm()
    return render(request, 'accounts/provide.html', {'form': form})

@login_required
def profile_view(request):
    """
    Displays the user’s current profile (including profile picture).
    """
    return render(request, 'accounts/profile.html')

@login_required
def upload_picture_view(request):
    """
    Displays and processes the form for uploading/updating the profile picture.
    """
    if request.method == 'POST':
        form = UserImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect('profile')  # Redirect back to profile page
        else:
            messages.error(request, "Error uploading your profile picture.")
    else:
        form = UserImageForm(instance=request.user)

    return render(request, 'accounts/upload_picture.html', {'form': form})

@login_required
def edit_profile_view(request):
    """
    Displays and processes the form for updating the user’s profile.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')  # Go back to the profile page
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def request_provider_view(request):
    user = request.user
    if not user.is_provider_approved:
        user.provider_requested = True
        user.save()
        messages.success(request, "Your request for provider status has been submitted.")
    else:
        messages.info(request, "You are already provider approved.")
    return redirect('choose')

@login_required
def manage_provider_requests_view(request):
    if not request.user.is_provider_approved and not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('choose')

    query = request.GET.get('q', '')
    pending_users = CustomUser.objects.filter(is_provider_approved=False).exclude(is_superuser=True)

    if query:
        pending_users = pending_users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    return render(request, 'accounts/manage_provider_requests.html', {'pending_users': pending_users, 'query': query})

@login_required
def approve_provider_view(request, user_id):
    # Only allow provider-approved users to approve requests.
    if not request.user.is_provider_approved:
        messages.error(request, "Access denied.")
        return redirect('choose')
    
    user_to_approve = get_object_or_404(CustomUser, id=user_id)
    user_to_approve.is_provider_approved = True
    user_to_approve.provider_requested = False  # (Optional, if you were using this field)
    user_to_approve.save()
    messages.success(request, f"{user_to_approve.username} has been approved as a provider.")
    return redirect('manage_provider_requests')
    
def borrow_view(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query)
        ).order_by('-created_at')
    else:
        books = Book.objects.all().order_by('-created_at')
    
    books = books.annotate(avg_rating=Avg('review__rating'))
    
    return render(request, 'accounts/borrow.html', {'books': books, 'query': query})

@login_required
def my_books_view(request):
    if not request.user.is_provider_approved:
        messages.error(request, "Access denied: You must be provider-approved to view your lending books.")
        return redirect('choose')

    books = Book.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'books/my_books.html', {'books': books})

@login_required
def delete_book_view(request, book_uuid):
    # only the owner should be able to delete
    book = get_object_or_404(Book, uuid=book_uuid, user=request.user)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted successfully.")
        return redirect('my_books')  # Assuming 'my_books' is the correct URL name for the user's books

    return render(request, 'books/confirm_delete.html', {'book': book})

@login_required
def edit_book_view(request, book_uuid):
    # only the owner should be able to edit
    book = get_object_or_404(Book, uuid=book_uuid, user=request.user)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully.")
            return redirect('my_books')  # Assuming 'my_books' is the correct URL name for the user's books
    else:
        form = BookForm(instance=book)

    return render(request, 'books/edit_book.html', {
        'form': form,
        'book': book
    })
