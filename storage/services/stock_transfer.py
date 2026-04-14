from storage.models import Stock
from django.db import transaction
from storage.services.movement_service import register_movement


@transaction.atomic
def stock_transfer(from_position, item, quantity, to_position, user=None):

    if not from_position or not to_position:
        raise ValueError("Origem e destino são obrigatórios")

    stock_from = Stock.objects.get(
        item=item,
        position=from_position
    )

    if stock_from.quantity < quantity:
        raise ValueError("Estoque insuficiente")

    stock_from.quantity -= quantity
    stock_from.save(update_fields=['quantity'])

    stock_to, _ = Stock.objects.get_or_create(
        item=item,
        position=to_position,
        defaults={'quantity': 0}
    )

    stock_to.quantity += quantity
    stock_to.save(update_fields=['quantity'])

    register_movement(
        user=user,
        item=item,
        quantity=quantity,
        movement_type='TRANSFER',
        from_position=from_position,
        to_position=to_position,
        description="Transferência entre posições"
    )