from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Dashboard_Message, Concept, Resource, Subject, Topic, TemporaryFileStorage, User

admin.site.register(Concept)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Resource)
admin.site.register(Dashboard_Message)
admin.site.register(TemporaryFileStorage)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Define admin model for custom User model with email and username fields.
    Base admin model can be found in django/contrib/auth/admin on line 41.
    """
    readonly_fields=(('date_joined',))
    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_creator','is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_joined','last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'date_joined')

admin.site.site_header = "Chiron Learning"