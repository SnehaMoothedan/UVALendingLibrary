from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home(request):
   return HttpResponse("<h1>Welcome! You are logged in.</h1>")

@login_required
def choose_view(request):
    if request.method == 'POST':
        choice = request.POST.get('choice')  # "provider" or "borrower"
        request.user.role = choice
        request.user.save()
        if choice == 'provider':
            return redirect('provide_page')
        else:
            return redirect('borrow_page')
    return render(request, 'accounts/choose.html')

@login_required
def post_login_redirect_view(request):
    # Assuming your user model has a field "role"
    # that can be "provider" or "borrower"
    role = getattr(request.user, 'role', None)

    if role == 'provider':
        return redirect('provide_page')
    elif role == 'borrower':
        return redirect('borrow_page')
    else:
        # If no role is set, maybe redirect them to a "choose" page or homepage
        return redirect('choose')