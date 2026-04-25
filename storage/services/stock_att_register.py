from decimal import Decimal
from django.db import transaction
from storage.models import StockLot
from storage.services.movement_service import register_movement


@transaction.atomic
def add_stock_lot(item, position, quantity, lot, expiration_date, user=None):
    quantity = Decimal(str(quantity))

    stocklot, _ = StockLot.objects.get_or_create(
        item=item,
        position=position,
        lot=lot,
        expiration_date=expiration_date,
        defaults={'quantity': 0}
    )

    stocklot.quantity += quantity
    stocklot.save(update_fields=['quantity'])

    register_movement(
        user=user,
        item=item,
        quantity=quantity,
        movement_type='IN',
        to_position=position,
        description=f"Entrada lote {lot}"
    )

    return stocklot

@transaction.atomic
def remove_stock_lot(stocklot, quantity, user=None):
    quantity = Decimal(str(quantity))

    if stocklot.quantity < quantity:
        raise ValueError("Estoque insuficiente")

    stocklot.quantity -= quantity
    stocklot.save(update_fields=['quantity'])

    register_movement(
        user=user,
        item=stocklot.item,
        quantity=quantity,
        movement_type='OUT',
        from_position=stocklot.position,
        description=f"Saída lote {stocklot.lot}"
    )

    return stocklot