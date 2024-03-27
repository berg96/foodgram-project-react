from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
