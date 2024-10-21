from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile

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
    
class ProfileForm(forms.ModelForm):
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
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary ring-secondary sm:text-sm sm:leading-6", "autocomplete": "email"})
    )
    
    bio = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "id":"bio",
                "class":"mt-1 block w-full border border-gray-300 rounded-md p-2",
            }
        ),
        required=False
    )
    
    dp = forms.ImageField(
        widget=forms.FileInput(attrs=
                               {"class": "block placeholder-primary w-full text-sm border border-gray-300 rounded-lg cursor-pointer bg-gray-50 mt-1 hidden", "aria-describedby": "file_input_help", "id": "file_input", "onchange": "previewImage(event)"}),
        required=False
    )
    
        
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={"id": "password", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )
    
    password1 = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput(attrs={"id": "password1", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )
            
    password2 = forms.CharField(
        label="Confirm Password",
        required=False,
        widget=forms.PasswordInput(attrs={"id": "password2", "class": "block w-full rounded-md border-0 py-1.5 ring-secondary text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-secondary sm:text-sm sm:leading-6", "autocomplete":"current-password", "placeholder": "password"})
    )
    
    class Meta:
        model = Profile
        fields = ['bio', 'dp']
         
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email == self.instance.user.email:
            return email
    
        # email must not be taken by another user
        if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
            self.add_error('email', "Email is aready taken")
            raise forms.ValidationError("This Email is already taken")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        password = cleaned_data.get('password')
        
        if (password1 or password2) and not password:
            raise forms.ValidationError("Fill required fields to change password")
        
        # if user entered old password validate the password change
        if password:
            if not self.instance.user.check_password(password):
                self.add_error('password', 'Old Password is not correct')
            if password1 and password1 != password2:
                self.add_error('password2', "Password Mismatch")
            if not password1:
                self.add_error('password1', "New Password can not be empty")
        
                
        return cleaned_data
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # update email if it is changed
        email = self.cleaned_data.get('email')
        if email and email != self.instance.user.email:
            self.instance.user.email = email
            
        # update the password if provided
        new_password = self.cleaned_data.get('password1')
        if new_password:
            self.instance.user.set_password(new_password)
            
        # update the first name
        first_name = self.cleaned_data.get('first_name')        
        if first_name and first_name != self.instance.user.first_name:
            self.instance.user.first_name = first_name
            
        # update the last name
        last_name = self.cleaned_data.get('last_name')
        if last_name and last_name != self.instance.user.last_name:
            self.instance.user.last_name = last_name
        
        self.instance.user.save()
            
        if commit:
            profile.save()
            
        return profile
            