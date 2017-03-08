from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import *
from django.forms import CharField
from django.forms import FileField
from django.forms import FileInput
from django.forms import Form
from django.forms import PasswordInput
from django.forms import TextInput

from .models import FileUpload, RequestFeedback


class LoginForm(AuthenticationForm):
    """
    Form for doing user login
    NOT USED
    """

    username = CharField(
        widget=TextInput(
            attrs={'class': 'mdl-textfield__input', 'id': 'username'}))
    password = CharField(
        widget=PasswordInput(
            attrs={'class': 'mdl-textfield__input', 'id': 'password'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError(
                'Sorry, username or password incorrect!')
        return self.cleaned_data


class ChangePasswordForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    NOT USED
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': ('Your old password was entered incorrectly. '
                               'Please enter it again.'),
    })
    old_password = forms.CharField(
        label=('Old password'),
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class NewPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    NOT USED
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = CharField(label=('New password'),
                              widget=PasswordInput(
                                  attrs={'class': 'mdl-textfield__input'}),
                              help_text=password_validation.password_validators_help_text_html())
    new_password2 = CharField(
        label=('New password confirmation'),
        widget=PasswordInput(attrs={'class': 'mdl-textfield__input'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class FileForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['CSVFile', ]

class FeedbackRequestForm(forms.ModelForm):
    class Meta:
        model = RequestFeedback
        fields = ['course', 'request_by', 'end_date']

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
        ]
    def save(self,commit=True):
        user = super(UserForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
