from decimal import Decimal
from django.db import transaction
from storage.models import StockMovement, Stock


def create_StockMovement(item, position, StockMovement_type, quantity):
    StockMovement.objects.create(
        item=item,
        position=position,
        StockMovement_type=StockMovement_type,
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
        create_StockMovement(item, position, 'IN', new_quantity)
        return stock

    diff = new_quantity - stock.quantity

    if diff == 0:
        return stock

    StockMovement_type = 'IN' if diff > 0 else 'OUT'
    create_StockMovement(item, position, StockMovement_type, abs(diff))

    stock.quantity = new_quantity
    stock.save(update_fields=['quantity'])

    return stock