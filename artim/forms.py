from django import forms
from accounts.models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.DecimalField(label='Rate from 0.0 to 5.0', widget=forms.TextInput(attrs={'id':'rating', 'required':'True'}))
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.TextInput(attrs={'placeholder':'Write a brief review', 'required':'True', 'style':'height: 100px'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if int(rating) > 5:
            raise forms.ValidationError(f"The highest rating is 5")
        return rating