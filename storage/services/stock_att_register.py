from decimal import Decimal
from django.db import transaction
from storage.models import Movement, Stock


def create_movement(item, position, movement_type, quantity):
    Movement.objects.create(
        item=item,
        position=position,
        movement_type=movement_type,
        quantity=quantity
    )


@transaction.atomic
def handle_stock(stock, new_quantity, item, position):
    new_quantity = Decimal(str(new_quantity))

    if not stock:
        stock = Stock.objects.create(
            item=item,
            position=position,
            quantity=new_quantity
        )
        create_movement(item, position, 'IN', new_quantity)
        return stock

    diff = new_quantity - stock.quantity

    if diff == 0:
        return stock

    movement_type = 'IN' if diff > 0 else 'OUT'
    create_movement(item, position, movement_type, abs(diff))

    stock.quantity = new_quantity
    stock.save(update_fields=['quantity'])

    return stock