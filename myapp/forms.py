from django import forms
from .models import Companies
from .models import Brands


class CompayForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'

class BrandForm(forms.ModelForm):
	class Meta:
		model = Brands
        fields = '__all__'

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes',
   widget=forms.FileInput(attrs={'multiple': True})
    )

class BrandEditForm(forms.ModelForm):
	class Meta:
		model = Brands
        fields = '__all__'
