from storage.models import StockMovement, Stock
from django.db import transaction

def stock_trasnfer(from_position, item, quantity, to_position):

    with transaction.atomic():
        if from_position:
            StockMovement.objects.create(
                item=item,
                position=from_position,
                StockMovement_type='OUT',
                quantity=quantity
            )
            stock_from = Stock.objects.get(
                item=item,
                position=from_position
            )
            stock_from.quantity -= quantity
            stock_from.sav      
        if to_position:
            StockMovement.objects.create(
                item=item,
                position=to_position,
                StockMovement_type='IN',
                quantity=quantity
            )
            stock_to, _ = Stock.objects.get_or_create(
                item=item,
                position=to_position,
                defaults={'quantity': 0}
            )
            stock_to.quantity += quantity
            stock_to.save()