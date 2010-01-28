from django.contrib import admin

from loginurl.models import Key

class KeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created', 'usage_left', 'expires')

admin.site.register(Key, KeyAdmin)

