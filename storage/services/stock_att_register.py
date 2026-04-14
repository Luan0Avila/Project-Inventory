from decimal import Decimal
from django.db import transaction
from storage.models import Stock
from storage.services.movement_service import register_movement


@transaction.atomic
def handle_stock(stock, new_quantity, item, position, user=None):
    new_quantity = Decimal(str(new_quantity))

    if not stock:
        stock = Stock.objects.create(
            item=item,
            position=position,
            quantity=new_quantity
        )

        register_movement(
            user=user,
            item=item,
            quantity=new_quantity,
            movement_type='IN',
            to_position=position,
            description="Criação de estoque"
        )

        return stock

    diff = new_quantity - stock.quantity

    if diff == 0:
        return stock

    if diff > 0:
        register_movement(
            user=user,
            item=item,
            quantity=diff,
            movement_type='IN',
            to_position=position,
            description="Ajuste de estoque (entrada)"
        )

    else:
        register_movement(
            user=user,
            item=item,
            quantity=abs(diff),
            movement_type='OUT',
            from_position=position,
            description="Ajuste de estoque (saída)"
        )

    # atualiza estoque
    stock.quantity = new_quantity
    stock.save(update_fields=['quantity'])

    return stock