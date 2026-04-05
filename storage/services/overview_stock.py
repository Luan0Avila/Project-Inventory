from storage.models import Stock

def overview(positions):
    stocks = Stock.objects.select_related('item', 'position')
    stock_map = {s.position_id: s for s in stocks}

    rows = []

    for position in positions:
        stock = stock_map.get(position.id)

        if stock and stock.quantity > 0:
            rows.append({
                'position': position,
                'item': stock.item,
                'quantity': stock.quantity,
                'empty': False
            })
        else:
            rows.append({
                'position': position,
                'item': None,
                'quantity': 0,
                'empty': True
            })

    return rows