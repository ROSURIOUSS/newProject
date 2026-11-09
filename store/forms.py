from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Order, Review

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('name', 'phone', 'delivery', 'address', 'time_slot', 'payment', 'email', 'comment')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Олена', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'placeholder': '+380 __ ___ __ __', 'autocomplete': 'tel'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
            'address': forms.TextInput(attrs={'placeholder': 'вул. Сумська 24, кв. 7, підʼїзд 2'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Без цибулі, подзвоніть за 10 хв'}),
            'delivery': forms.RadioSelect(),
            'time_slot': forms.RadioSelect(),
            'payment': forms.RadioSelect(),
        }
        labels = {
            'address': 'Адреса доставки',
            'time_slot': 'Коли привезти',
            'payment': 'Спосіб оплати',
            'delivery': 'Як отримаєте',
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Вкажіть коректний номер телефону')
        return phone

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('delivery') == Order.DELIVERY_DELIVERY:
            address = (cleaned.get('address') or '').strip()
            if len(address) < 6:
                self.add_error('address', 'Вкажіть вулицю, будинок і квартиру')
        return cleaned

class SignUpForm(UserCreationForm):
    """Реєстрація: логін, email, імʼя + пароль двічі."""
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label="Імʼя", max_length=60, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['username'].help_text = 'Латиниця, цифри та @/./+/-/_'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Пароль ще раз'
        self.fields['password1'].help_text = 'Мінімум 8 символів, не лише цифри'
        self.fields['password2'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'ваш_логін'
        self.fields['email'].widget.attrs['placeholder'] = 'you@example.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Олена'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Користувач із таким email вже є')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін'
        self.fields['password'].label = 'Пароль'
        self.fields['username'].widget.attrs['placeholder'] = 'ваш_логін'
        self.fields['password'].widget.attrs['placeholder'] = '••••••••'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Що сподобалось, а що можна покращити?',
            }),
        }
