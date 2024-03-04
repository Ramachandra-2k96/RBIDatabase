from django.contrib import admin
from .models import Bank

class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'owner_name', 'bank_type','password')
    search_fields = ('name', 'owner_name', 'code')
    list_filter = ('bank_type',)

admin.site.register(Bank, BankAdmin)
