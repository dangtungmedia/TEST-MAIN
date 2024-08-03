from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


def delete_selected(modeladmin, request, queryset):
    for user in queryset:
        user.delete()  # Gọi phương thức delete() của mỗi người dùng

delete_selected.short_description = "Xóa người dùng đã chọn"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    actions = [delete_selected]
    list_display = ('username', 'is_staff', 'is_active',)
    list_filter = ('username', 'is_staff', 'is_active',)

    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'note_password','full_name','bank_number','phone_number')}),  # Add 'email' and 'image_path'
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_editor','is_deleted','user_permissions')}),
        ('Groups', {'fields': ('groups',)}),
        # Add any other fieldsets you want here
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'note_password','is_staff', 'is_active','is_editor','is_deleted')}  # Add 'email'
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
