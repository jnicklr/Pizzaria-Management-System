from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest # Biblioteca para criar um painel administrativo
from .models import User # Biblioteca para criar modelos de tabelas
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AdminPasswordChangeForm

class UserCreationForm(forms.ModelForm):
    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'nome')

    # O método abaixo é para verificar se as senhas são iguais
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    # O método abaixo é para salvar o usuário
    def save(self, commit=True):
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

    password = ReadOnlyPasswordHashField(label=("Password"),
        help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))

    class Meta:
        model = User
        fields = ('nome', 'email', 'password', 'cpf', 'genero', 'estado_civil', 'telefone', 'is_active', 'is_staff', 'is_superuser')

class ReadOnlyAdminMixin:
    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False
    
    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if request.user.is_superuser:
            return True
        return False
    
    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False

@admin.register(User) # Decorator para registrar a classe no painel administrativo
class UserAdmin(ReadOnlyAdminMixin, BaseUserAdmin): # Classe para listar os usuários no painel administrativo

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('nome', 'email', 'cpf') # Lista os campos que serão exibidos
    search_fields = ['nome']
    ordering = ['nome']
    fieldsets = [
        (
            'Cadastro de Usuário', {
                "fields": ['nome', 'email', 'password']
            }
        ),
        (
            "Campos Extras", {
                "classes": ["collapse"],
                "fields": ['cpf', 'genero', 'estado_civil', 'telefone']
            }
        ),
        (
            "Opções Avançadas", {
                "classes": ["collapse"],
                "fields": ['is_active', 'is_staff', 'is_superuser', "groups", "user_permissions",]
            }
        )
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nome', 'email', 'password1', 'password2'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['is_active'].hidden_widget()
            form.base_fields['is_staff'].disabled = True
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['groups'].disabled = True
            form.base_fields['user_permissions'].disabled = True
        return form
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(id = request.user.id)
        return queryset