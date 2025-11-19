from django import forms

class RecommendForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)

from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '請輸入您的姓名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '請輸入您的電子郵件'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '請輸入您想要告訴我們的訊息'}),
        }