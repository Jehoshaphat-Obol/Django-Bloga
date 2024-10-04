from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from .forms import SignInForm,  SignUpForm

def sign_up_view(request):
    """A function based view to register users
    
    Keyword arguments:
    request -- client request
    
    Return: HttpResponse
    """
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Hello {user.first_name} {user.last_name}, Welcome to Bloga 🎊")
            return redirect("blog:home")
    
        messages.error(request, f"{", ".join(form.error_messages)}")
        
    context = {
        "form": form,
    }
    return render(request, 'authentication/signup.html', context=context)


def sign_in_view(request):
    """A function based view for signing users in
    
    Keyword arguments:
    request -- Clients Request
    Return: HttpResponse
    """
    
    form = SignInForm()
    
    if request.method == "POST":
        form = SignInForm(request=request, data = request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # authenticate the user
            user  = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back {user.first_name} {user.last_name}")
                return redirect("blog:home")
        
            
        print(form.error_messages)
        messages.error(request, "Invalid username or password")
    
    context = {
        "form": form,
    }
    return render(request, 'authentication/signin.html', context)
    
def sign_out_view(request):
    """A function based view for signing users out
    
    Keyword arguments:
    request -- Clients Request
    Return: HttpResponse
    """
    logout(request)
    return redirect('authentication:sign_in')