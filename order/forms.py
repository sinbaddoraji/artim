from django import forms
from .models import Withdrawal


class AddFundsForm(forms.Form):
    amount = forms.CharField(label='Enter an amount below £500', widget=forms.TextInput(attrs={'id':'amount', 'required':'True'}))

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if int(amount) > 500:
            raise forms.ValidationError(f"You can only add a maximun amount of £500")
        elif int(amount) < 10:
            raise forms.ValidationError(f"You can only add a minimum amount of £10")
        return amount


# class WithdrawalForm(forms.ModelForm):
#     amount = forms.CharField(label='Enter an amount below £500', widget=forms.TextInput(attrs={'id':'amount', 'required':'True'}))
#     method = forms.Charfield()
#     class Meta:
#         model = Withdrawal
#         exclude = ['artisanwithdrawal', 'withdrawal_date']
#         widgets = {
#             'phone_number': forms.TextInput(attrs={'id':'phone_number', 'maxlength':11, 'onkeypress':'return (event.charCode !==8 && event.charCode ===0 || (event.charCode >= 48 && event.charCode <= 57))'}),
#         }


#     def clean_amount(self):
#         amount = self.cleaned_data['amount']
#         if int(amount) > 500:
#             raise forms.ValidationError(f"You can only add a maximun amount of £500")
#         elif int(amount) < 10:
#             raise forms.ValidationError(f"You can only add a minimum amount of £10")
#         return amount