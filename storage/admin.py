from django.contrib import admin
from .models import Position, Item, Stock, Movement

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'is_occupied')
    search_fields = ('position',)

    def is_occupied(self, obj):
        return obj.stock_set.filter(quantity__gt=0).exists()

    is_occupied.boolean = True
    is_occupied.short_description = 'Ocupada'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'description')
    search_fields = ('code', 'description')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'position', 'quantity')
    list_filter = ('position', 'item')
    search_fields = ('item__code', 'position__position')

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'position', 'movement_type', 'quantity', 'created_at')
    list_filter = ('movement_type', 'position', 'item')
    search_fields = ('item__code',)
    readonly_fields = ('created_at',)
