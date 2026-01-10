from django.contrib import admin
from .models import Position, Item

class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'occupied')
    search_fields = ('position',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'position')
    search_fields = ('code',)

admin.site.register(Position, PositionAdmin)
admin.site.register(Item)