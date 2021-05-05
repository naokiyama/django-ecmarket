from django.contrib import admin
from .models import Accounts
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class AccountsAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'username',
                    'email', 'data_joined', 'last_login', 'is_active')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Accounts, AccountsAdmin)
