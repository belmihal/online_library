from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "status", "borrowed_at", "due_at", "returned_at")
    list_filter = ("status", "borrowed_at")
    search_fields = ("user__username", "book__title")
