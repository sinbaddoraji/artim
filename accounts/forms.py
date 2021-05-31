from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate

GENDER = [
    ('male', 'Male'),
    ('female', 'Female')
]


USER_TYPE = [
    ('customer', 'Customer'),
    ('artisan', 'Artisan')
]

SKILLS = [ 
    ('plumber','Plumber'), 
    ('butcher','Butcher'), 
    ('electrician','Electrician'),
    ('gardener','Gardener'), 
    ('jeweller','Jeweller'),('roofer','Roofer'), 
    ('bricklayer','Bricklayer'),('baker','Baker'),('tailor','Tailor'),
    ('carpenter','Carpenter'), ('gem-cutter','Gem-Cutter'),
    ('printer', 'Printer'), ('veterinarian','Veterinarian'), 
    ('decorator','Decorator'), ('waller','Waller'), 
    ('thatcher','Thatcher'),('slater','Slater'), 
    ('glazier','Glazier'), ('shearer','Shearer'), ('hair braider','Hair Braider'),
    ('hair barber','Hair Barber'), ('car painter','Car Painter'),
    ('mechanic', 'Mechanic')
    ]

class UserLoginForm(forms.Form):
    error_messages = {
        'invalid_login': ("Please enter a valid username and password combination. "),
        'inactive': ("This account is inactive."),
    }
    username = forms.CharField(max_length=20, widget=forms.TextInput({'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput({'placeholder':'Password'}))

    def clean_username(self):
        un = self.cleaned_data['username']
        if len(un) == 0:
            raise forms.ValidationError("Please enter your username.")
        return un

    def clean_password(self):
        pw = self.cleaned_data['password']
        if len(pw) == 0:
            raise forms.ValidationError("Please enter your password.")
        return pw


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'placeholder':'Confirm password'}))
    username = forms.SlugField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username','email', 'password', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder':'First Name', 'required':'True'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Last Name', 'required':'True'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'required':'True'}),
        }


    def clean_first_name(self):
        fn = self.cleaned_data['first_name']
        if fn.isalpha() == False:
            raise forms.ValidationError("Your First Name must be all letters.")
        elif len(fn) < 2:
            raise forms.ValidationError("First name is too short.")
        return fn

    def clean_last_name(self):
        ln = self.cleaned_data['last_name']
        if ln.isalpha() == False:
            raise forms.ValidationError("Your Last Name must be all letters.")
        elif len(ln) < 2:
            raise forms.ValidationError("Last name is too short.")
        return ln

    def clean_email(self):
        email = self.cleaned_data['email']
        email_count = User.objects.filter(email=email).count()
        if email_count > 0:
            raise forms.ValidationError("Someone already used this email, please use another one.")
        return email

    def clean_username(self):
        un = self.cleaned_data['username']
        username_count = User.objects.filter(username=un).count()
        if un[0].isdigit() == True:
            raise forms.ValidationError("Your Username can't start with a number.")
        elif username_count > 0:
            raise forms.ValidationError("Username is taken, please use another one.")
        return un

    def clean_password(self):
        pw = self.cleaned_data['password']
        if len(pw) < 4:
            raise forms.ValidationError("Password is too short")
        return pw
    
    def clean(self):
        all_clean = super().clean()
        pw = all_clean.get("password")
        pw2 = all_clean.get("password2")

        if pw != pw2:
            raise forms.ValidationError("Passwords don't match.")

class UserProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER, required=True, widget=forms.Select())
    user_type = forms.ChoiceField(label='What type of user are you?', widget=forms.RadioSelect(attrs={'id':'user_type', 'onchange':'toggler()'}), choices=USER_TYPE, required=True)
    age = forms.IntegerField(max_value=120)
    photo = forms.ImageField(label='Profile picture', required=False)
    services = forms.MultipleChoiceField(label='', choices=SKILLS, help_text='', widget=forms.SelectMultiple(attrs={'id':'services'}))
    phone_number = forms.CharField()
    price = forms.DecimalField(label='Price per hour')

    class Meta:
        model = UserProfile
        exclude = ['user', 'payment_details', 'bank_details', 'slug', 'artisan_approved', 'blocked']
        widgets = {
            'phone_number': forms.TextInput(attrs={'id':'phone_number', 'maxlength':11, 'onkeypress':'return (event.charCode !==8 && event.charCode ===0 || (event.charCode >= 48 && event.charCode <= 57))'}),
        }

    def clean_services(self):
        services = self.cleaned_data['services']
        if len(services) > 4:
            raise forms.ValidationError(f"You can't select more than 4 services (You selected {len(services)})")
        return services

    def clean(self):
        all_clean = super().clean()
        user_type = all_clean.get("user_type")
        services = all_clean.get("services")
        if user_type == "artisan" and len(services) < 1:
            raise forms.ValidationError("You have to choose at least one service as an ARTISAN")
