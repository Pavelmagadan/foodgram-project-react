from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
# from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_superuser'
    )
    list_display_links = (
        'pk', 'email', 'username', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_superuser'
    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('pk',)




# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm
# from .models import User

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     model = User


# admin.site.register(User, CustomUserAdmin)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = (
#         'pk', 'email', 'username', 'first_name', 'last_name',
#         'is_staff', 'is_active', 'is_superuser'
#     )
#     list_display_links = (
#         'pk', 'email', 'username', 'first_name', 'last_name',
#         'is_staff', 'is_active', 'is_superuser'
#     )
#     search_fields = ('username',)
#     ordering = ('pk',)
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
#         (_('Permissions'), {
#             'fields': ('is_active', 'is_staff', 'is_superuser'),
#         }),
#     )
