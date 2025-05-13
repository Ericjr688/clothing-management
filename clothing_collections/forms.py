from django import forms
from .models import Collection

# class SearchForm(forms.Form):
#     keyword = forms.CharField(
#         label='Search keywords',
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user and self.user.userprofile.role == 'patron' and not self.instance.pk:
            self.fields['visibility'].choices = [
                ('public', 'Public'),
            ]