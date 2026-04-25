from storage.models import StockLot
from django.db.models import Sum


def overview(positions):
    stocklots = (
        StockLot.objects
        .select_related('item', 'position')
        .order_by('position_id')
    )

    # agrupa por posição
    position_map = {}

    for lot in stocklots:
        if lot.position_id not in position_map:
            position_map[lot.position_id] = {
                'items': [],
                'total_quantity': 0
            }

        position_map[lot.position_id]['items'].append({
            'item': lot.item,
            'quantity': lot.quantity,
            'lot': lot.lot,
            'expiration_date': lot.expiration_date
        })

        position_map[lot.position_id]['total_quantity'] += lot.quantity

    rows = []

    for position in positions:
        data = position_map.get(position.id)

        if data:
            rows.append({
                'position': position,
                'items': data['items'],  # 🔥 agora é lista
                'total_quantity': data['total_quantity'],
                'empty': False
            })
        else:
            rows.append({
                'position': position,
                'items': [],
                'total_quantity': 0,
                'empty': True
            })

    return rows