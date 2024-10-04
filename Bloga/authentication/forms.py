from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    """Form used to sign up new users
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "first name", "placeholder": "First Name"})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "last name", "placeholder": "Last Name"})
    )
    
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "username", "placeholder": "username"})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "email"})
    )
    
    password1 = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={"id": "password1", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )
            
    password2 = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"id": "password2", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2']
        
    def save(self, commit=True):
        """Function used to save the form data to the user model
        
        Keyword arguments:
        commit -- boolean argument, when false form data is not saved to the database else it is saved
        Return: user
        """
        
        user = super(SignUpForm, self).save(commit=False)
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        
        return user
    
class SignInForm(AuthenticationForm):
    """Form used to authenticate users
    """
    
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "username", "placeholder": "username"})
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"id": "password1", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )