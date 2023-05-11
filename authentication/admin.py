# Django documentation : Si vous utilisez une classe ModelAdmin personnalisée qui hérite de
# django.contrib.auth.admin.UserAdmin, vous devez alors ajouter vos champs personnalisés à
# fieldsets (pour les champs qui doivent faire partie de l’édition des utilisateurs) et à
# add_fieldsets (pour les champs qui doivent faire partie de la création des utilisateurs).
# Par exemple …

# I copy-pasted the code of the django documentation example and provided some changes
# https://docs.djangoproject.com/fr/4.1/topics/auth/customizing/#a-full-example
# Voici un exemple d’application d’utilisateur personnalisé compatible avec l’interface d’administration.

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

# from customauth.models import MyUser
from authentication.models import User as MyUser


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        # fields = ('email', 'birth_date')
        fields = ('username', 'email', 'password', 'birth_date')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        # fields = ('email', 'password', 'date_of_birth', 'is_active', 'is_admin')
        fields = ('username', 'email', 'password', 'birth_date')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    # list_display = ('email', 'team', 'is_admin')
    list_display = ('id', 'username', 'email', 'birth_date')

    # list_filter = ('is_admin',)

    fieldsets = (
        # (None, {'fields': ('email', 'password')}),
        (None, {'fields': ('username', 'password', 'birth_date')}),
        # ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Personal info', {'fields': ('email',)}),
        # ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')})


    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # 'fields': ('email', 'date_of_birth', 'password1', 'password2'),
            'fields': ('username', 'password1', 'password2', 'birth_date'),
        }),
        # ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Personal info', {'fields': ('email',)}),
        # ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')})
    )
    # search_fields = ('email',)
    search_fields = ('username',)
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
