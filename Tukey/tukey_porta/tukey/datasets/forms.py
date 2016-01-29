from django import forms
from .models import DataSet, KeyValue

#right way to remove the attrs redundancy?
class UpdateDataSetForm(forms.Form): 

    def __init__(self, *args, **kwargs):
        #should check that this exists
        keyvalues = kwargs.pop('keyvalues')
        super(UpdateDataSetForm, self).__init__(*args, **kwargs)

        for keyvalue in keyvalues:
            if keyvalue.key.key_name == 'description': 
                self.fields['kv_%s' % keyvalue.id] = forms.CharField(label=keyvalue.key.key_name, initial=keyvalue.value, widget=forms.Textarea(attrs={'class': 'span5'}))
            elif keyvalue.key.key_name == 'short_description':
                self.fields['kv_%s' % keyvalue.id] = forms.CharField(label=keyvalue.key.key_name, initial=keyvalue.value, widget=forms.Textarea(attrs={'class': 'span5', 'rows' : '5'}))
            elif keyvalue.key.key_name == 'modified':
                self.fields['kv_%s' % keyvalue.id] = forms.DateTimeField(label=keyvalue.key.key_name, initial=keyvalue.value, widget=forms.DateTimeInput(attrs={'class': 'span5'}))
            else:
                self.fields['kv_%s' % keyvalue.id] = forms.CharField(label=keyvalue.key.key_name, initial=keyvalue.value, widget=forms.TextInput(attrs={'class': 'span5'}))

    def keyvalues_id_value(self):
        for name, value in self.cleaned_data.items():
            key_id = name.split('_')[1]
            yield (key_id, value)

class AddDataSetForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        keys = kwargs.pop('keys')
        super(AddDataSetForm, self).__init__(*args, **kwargs)

        for key in keys:
            #Just require title for now
            if key.key_name == 'title':
                self.fields[key.key_name] = forms.CharField(widget=forms.TextInput(attrs={'class': 'span5'}))
            elif key.key_name == 'description': 
                self.fields[key.key_name] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'span5'}))
            elif key.key_name == 'short_description':
                self.fields[key.key_name] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'span5', 'rows' : '5'}))
            elif key.key_name == 'modified':
                self.fields[key.key_name] = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'span5'}))
            else:
                self.fields[key.key_name] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'span5'}))

#class AddKeyValueForm(forms.Form):
