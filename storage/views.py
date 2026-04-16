from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock, Position, Stock, StockMovement, Item
from django.db.models import Exists, OuterRef
from django.contrib import messages
from django.db import transaction
from storage.models import StockMovement
from .forms import StockMovementForm
from .forms import PositionAdjustForm
from django.contrib.auth.decorators import login_required
from storage.services.validation_movment import validation_movement
from storage.services.stock_transfer import stock_transfer
from storage.services.stock_att_register import handle_stock
from storage.services.overview_stock import overview
from django.core.paginator import Paginator

def home(request):
    return render(request, 'storage/pages/home.html')

@login_required
def storage_map(request):
    positions = Position.objects.annotate(
        has_stock=Exists(
            Stock.objects.filter(position=OuterRef('pk'), quantity__gt=0)
        )
    )

    return render(request, 'storage/pages/map.html', {
        'positions': positions
    })

@login_required
def position_detail(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    stock = Stock.objects.filter(position=position).select_related('item').first()
    items = Item.objects.all()

    if request.method == 'POST':
        item_id = request.POST.get('item')
        new_quantity = float(request.POST.get('quantity'))

        item = Item.objects.get(id=item_id)

        validation_movement(stock, new_quantity, item, position)

        messages.success(request, 'Posição atualizada com sucesso')
        return redirect('storage:position_detail', position_id=position.id)

    return render(request, 'storage/pages/position_detail.html', {
        'position': position,
        'stock': stock,
        'items': items
    })

@login_required
def stock_movement(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['item']
            quantity = form.cleaned_data['quantity']
            from_position = form.cleaned_data['from_position']
            to_position = form.cleaned_data['to_position']

            stock_transfer(from_position, item, quantity, to_position)

            messages.success(request, 'Movimentação realizada com sucesso!')
            return redirect('storage:stock_movement')
    else:
        form = StockMovementForm()

    return render(request, 'storage/pages/movement_form.html', {
        'form': form
    })
@login_required
def stock_overview(request):
    edit_id = request.GET.get('edit')

    if request.method == 'POST':
        position_id = request.POST.get('position_id')
        item_id = request.POST.get('item')
        new_quantity = float(request.POST.get('quantity'))

        position = Position.objects.get(id=position_id)
        item = Item.objects.get(id=item_id)

        stock = Stock.objects.filter(position=position).first()

        handle_stock(stock, new_quantity, item, position, user=request)
        
        messages.success(request, 'Estoque atualizado')
        return redirect('storage:stock_overview')

    positions = Position.objects.all()
    items = Item.objects.all()
    
    rows = overview(positions)

    return render(request, 'storage/pages/stock_overview.html', {
        'rows': rows,
        'items': items,
        'editing_position_id': int(edit_id) if edit_id else None
    })

@login_required
def position_edit(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    stock = Stock.objects.filter(position=position).first()

    if request.method == 'POST':
        form = PositionAdjustForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['item']
            new_quantity = form.cleaned_data['quantity']


            with transaction.atomic(): # ver possibilidade de refatoração dentro de um função apenas para essa movimentação
                if stock:
                    diff = new_quantity - stock.quantity

                    if diff > 0:
                        StockMovement.objects.create(
                            item=item,
                            position=position,
                            movement_type='IN',
                            quantity=diff
                        )
                    elif diff < 0:
                        StockMovement.objects.create(
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

                    StockMovement.objects.create(
                        item=item,
                        position=position,
                        movement_type='IN',
                        quantity=new_quantity
                    )

            messages.success(request, 'Posição atualizada com sucesso')
            return redirect('storage:stock_overview')
    else:
        form = PositionAdjustForm(initial={
            'item': stock.item if stock else None,
            'quantity': stock.quantity if stock else 0
        })

    return render(request, 'storage/pages/position_edit.html', {
        'position': position,
        'form': form
    })

@login_required
def movement_history(request):
    movements = StockMovement.objects.select_related(
        'item', 'user', 'from_position', 'to_position'
    ).order_by('-created_at')

    # filtros
    item = request.GET.get('item')
    movement_type = request.GET.get('type')

    if item:
        movements = movements.filter(item__id=item)

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # paginação (depois dos filtros)
    paginator = Paginator(movements, 20)
    page = request.GET.get('page')
    movements = paginator.get_page(page)

    return render(request, "storage/pages/movement_history.html", {
        "movements": movements
    })