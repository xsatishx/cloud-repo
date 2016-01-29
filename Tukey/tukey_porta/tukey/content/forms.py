from django import forms
from tukey.content.models import Page

class PageForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'span10', 'rows' : 30}), required=False)
    slug = forms.CharField(required=False)
    nav_name = forms.CharField(required=False)
    nav_order = forms.CharField(required=False)
    img = forms.CharField(required=False)
    img_alt = forms.CharField(required=False)
    
    class Meta:
        model = Page