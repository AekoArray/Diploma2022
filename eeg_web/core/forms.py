from django.contrib.auth.models import User
from django.forms import ModelForm


class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __str__(self):
        return self.username

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
