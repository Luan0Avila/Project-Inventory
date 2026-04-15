from storage.models import StockMovement

def register_movement( 
    # adicionar exceções para quando realizar movimentações inválidas
    # Adicionar posições de kanban e de recebimento para itens não sumirem em movimentações
    *,
    user,
    item,
    quantity,
    movement_type,
    from_position=None,
    to_position=None,
    description=""
):
    StockMovement.objects.create(
        user=user,
        item=item,
        quantity=quantity,
        movement_type=movement_type,
        from_position=from_position,
        to_position=to_position,
        description=description
    )