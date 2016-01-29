from django import forms
import datetime
from django.forms import ModelForm
from tukey.keyservice.models import Repository, Key

class ARKForm(forms.Form):
    ark_key = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={'class' : 'span4'}))


class RepositoryForm(ModelForm):
	class Meta:
		model = Repository

class KeyForm(ModelForm):
	class Meta:
		model = Key


AVAILABILITY_TYPES = (
    ('open','open'),
    ('restricted','restricted'),
)

class MetadataForm(forms.Form):
    title = forms.CharField(label='Title*',
        max_length=200,widget=forms.TextInput(attrs={'class':'span4'}))

    investigator_name = forms.CharField(label='Investigator name*',
        max_length=200,widget=forms.TextInput(attrs={'class':'span4'}))
    investigator_affiliation =  forms.CharField(label='Investigator affiliation*',
        max_length=200,widget=forms.TextInput(attrs={'class':'span4'}))
    email = forms.EmailField(label='Email*',
        widget=forms.TextInput(attrs={'class':'span4'}))
    size = forms.CharField(label='Size*',
        max_length=200,widget=forms.TextInput(attrs={'class':'span4'}))

    description =  forms.CharField(label='Description*',
        widget=forms.Textarea(attrs={'class':'span4'}))
    date_collected = forms.DateField(label='Date collected*',
        initial=datetime.date.today)
    date_updated = forms.DateField(label='Date updated*',
        initial=datetime.date.today)
    date_uploaded = forms.DateField(label='Date uploaded',required=False,
        initial=datetime.date.today)

    keywords = forms.CharField(label='Keywords (for example, MeSH terms or other keywords used by journals for indexing, separated by commas)*',widget=forms.TextInput(attrs={'class':'span4'}))
    availability_type = forms.ChoiceField(label='Availabiliy type*',
        widget=forms.Select(attrs={'class' : 'span4'}), choices=AVAILABILITY_TYPES)
    availability_mechanism = forms.CharField(label='Availability mechanism',required=False,
        widget=forms.TextInput(attrs={'class':'span4'}))
    grant_or_support_source_and_id = forms.CharField(label='Grant/Support Source and ID*',widget=forms.TextInput(attrs={'class':'span4'}))
    acknowledgements = forms.CharField(label='Acknowledgements*',
        widget=forms.TextInput(attrs={'class':'span4'}))

    publications = forms.CharField(label='Publications*',
        widget=forms.TextInput(attrs={'class':'span4'}))

    url = forms.CharField(label='URL (to existing data location)',required=False,
        widget=forms.TextInput(attrs={'class':'span4'}))

