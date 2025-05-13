from django import forms
from .models import ClothingItem, ClothingItemImage, Review, Tag

class SearchForm(forms.Form):
    keyword = forms.CharField(
         label='Search keywords',
         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter keywords...'})
    )

class ClothingItemForm(forms.ModelForm):
    category = forms.ChoiceField(choices=Tag.ARTICLE_TYPES, required=False)
    size = forms.ChoiceField(choices=Tag.SIZES, required=False)
    color = forms.ChoiceField(choices=Tag.COLORS, required=False)

    class Meta:
        model = ClothingItem
        fields = ['name', 'description', 'image', 'availability', 'location']

    def save(self, commit=True):
        clothing_item = super().save(commit=False)
        clothing_item.save()
        clothing_item.tags.clear()

        category = self.cleaned_data.get('category')
        size = self.cleaned_data.get('size')
        color = self.cleaned_data.get('color')

        if category or size or color:
            tag, created = Tag.objects.get_or_create(
                category=category,
                size=size,
                color=color
            )
            clothing_item.tags.add(tag)

        return clothing_item

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ClothingItemImageForm(forms.ModelForm):
    class Meta:
        model = ClothingItemImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class':'form-control'})
        }
