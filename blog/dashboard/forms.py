from django import forms
from django.utils.translation import ugettext_lazy as _

from blog.dashboard.models import SiteConfiguration
from blog.models import CustomUser, Article
from blog.utils import STATUS_CHOICES


class UserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['nickname', 'biographical_info', 'role']


class AddUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['email', 'nickname', 'biographical_info', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('This email address is already registered.'))
        return email


class ArticleForm(forms.ModelForm):

    def __init__(self, request_user, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.request_user = request_user

    def save(self, commit=True):
        instance = super(ArticleForm, self).save(commit=False)
        if not hasattr(instance, 'author'):
            instance.author = self.request_user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'status', 'author']


class ArticleAuthorForm(ArticleForm):

    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'status']


CONTRIBUTOR_STATUS__CHOICES = [(STATUS_CHOICES[o], dict(
    Article.STATUS_CHOICES_TUPLE).get(STATUS_CHOICES[o], '')) for o in ['Draft', 'Pending']]


class ArticleContributorForm(ArticleForm):

    def __init__(self, request_user, *args, **kwargs):
        super(ArticleContributorForm, self).__init__(
            request_user, *args, **kwargs)
        self.fields['status'] = forms.ChoiceField(
            choices=CONTRIBUTOR_STATUS__CHOICES)

    # Avoid hacks
    def clean_status(self):
        data = self.cleaned_data['status']
        if int(data) not in [STATUS_CHOICES['Pending'], STATUS_CHOICES['Draft']]:
            raise forms.ValidationError("Incorrect value")
        return data

    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'status']


class ProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['nickname', 'biographical_info']


class ConfigurationForm(forms.ModelForm):

    class Meta:
        model = SiteConfiguration
