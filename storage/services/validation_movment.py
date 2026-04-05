from storage.models import Movement, Stock
from django.db import transaction
from decimal import Decimal

def validation_movment(stock, new_quantity, item, position):
    with transaction.atomic():

        new_quantity = Decimal(str(new_quantity))

        if stock:
            diff = new_quantity - stock.quantity

            if diff > 0:
                Movement.objects.create(
                    item=item,
                    position=position,
                    movement_type='IN',
                    quantity=diff
                )
            elif diff < 0:
                Movement.objects.create(
                    item=item,
                    position=position,
                    movement_type='OUT',
                    quantity=abs(diff)
                )

            stock.quantity = new_quantity
            stock.save()

        else:
            Stock.objects.create(
                item=item,
                position=position,
                quantity=new_quantity
            )

            Movement.objects.create(
                item=item,
                position=position,
                movement_type='IN',
                quantity=new_quantity
            )