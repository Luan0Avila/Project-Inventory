from storage.models import StockLot
from django.db import transaction
from decimal import Decimal
from storage.services.movement_service import register_movement


@transaction.atomic
def adjust_stock_lot(stocklot, new_quantity, user=None):
    new_quantity = Decimal(str(new_quantity))

    diff = new_quantity - stocklot.quantity

    if diff == 0:
        return stocklot

    # 📥 Entrada (aumentou)
    if diff > 0:
        register_movement(
            user=user,
            item=stocklot.item,
            quantity=diff,
            movement_type='IN',
            to_position=stocklot.position,
            description=f"Ajuste lote {stocklot.lot} (entrada)"
        )

    # 📤 Saída (diminuiu)
    else:
        register_movement(
            user=user,
            item=stocklot.item,
            quantity=abs(diff),
            movement_type='OUT',
            from_position=stocklot.position,
            description=f"Ajuste lote {stocklot.lot} (saída)"
        )

    stocklot.quantity = new_quantity
    stocklot.save(update_fields=['quantity'])

    return stocklot