from django.contrib import admin
from .models import Position, Item, StockLot, StockMovement

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

@admin.register(StockLot)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'position', 'quantity')
    list_filter = ('position', 'item')
    search_fields = ('item__code', 'position__position')

@admin.register(StockMovement)
class MovementAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'movement_type',
        'quantity',
        'from_position',
        'to_position',
        'user',
        'created_at'
    )

    list_filter = (
        'movement_type',
        'from_position',
        'to_position',
        'created_at'
    )
