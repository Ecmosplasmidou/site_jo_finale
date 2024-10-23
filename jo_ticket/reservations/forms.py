from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
        def save(self, commit=True):
            user = super().save(commit=False)
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
            return user
        
class ContactUsForm(forms.Form):
    nom = forms.CharField(required=False,  max_length=50)
    email = forms.EmailField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)