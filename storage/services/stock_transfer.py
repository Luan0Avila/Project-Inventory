from django.db import transaction
from decimal import Decimal
from storage.models import StockLot
from storage.services.movement_service import register_movement


@transaction.atomic
def stock_transfer(from_position, item, quantity, to_position, user=None):
    quantity = Decimal(str(quantity))

    if not from_position or not to_position:
        raise ValueError("Origem e destino são obrigatórios")

    # pega lotes ordenados por validade (FIFO)
    lots = (
        StockLot.objects
        .filter(item=item, position=from_position, quantity__gt=0)
        .order_by('expiration_date')
    )

    total_available = sum(l.quantity for l in lots)

    if total_available < quantity:
        raise ValueError("Estoque insuficiente")

    remaining = quantity

    for lot in lots:
        if remaining <= 0:
            break

        move_qty = min(lot.quantity, remaining)

        # 🔻 remove da origem
        lot.quantity -= move_qty
        lot.save(update_fields=['quantity'])

        # 🔺 adiciona no destino (mesmo lote e validade)
        dest_lot, _ = StockLot.objects.get_or_create(
            item=item,
            position=to_position,
            lot=lot.lot,
            expiration_date=lot.expiration_date,
            defaults={'quantity': 0}
        )

        dest_lot.quantity += move_qty
        dest_lot.save(update_fields=['quantity'])

        remaining -= move_qty

    # 🧾 log único
    register_movement(
        user=user,
        item=item,
        quantity=quantity,
        movement_type='TRANSFER',
        from_position=from_position,
        to_position=to_position,
        description="Transferência (FIFO por validade)"
    )