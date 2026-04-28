from django.shortcuts import render, redirect, get_object_or_404
from .models import StockLot, Position, StockMovement, Item
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
from django.db.models import Q, Sum, Count

def home(request):
    return render(request, 'storage/pages/home.html')

@login_required
def storage_map(request):
    positions = Position.objects.annotate(
        has_stock=Exists(
            StockLot.objects.filter(item=item, position=position)
        )
    )

    return render(request, 'storage/pages/map.html', {
        'positions': positions
    })

@login_required
def position_detail(request, position_id):
    position = get_object_or_404(Position, id=position_id)

    # 🔥 todos os lotes da posição
    stocklots = (
        StockLot.objects
        .filter(position=position)
        .select_related('item')
        .order_by('expiration_date')
    )

    items = Item.objects.all()

    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')
        lot = request.POST.get('lot')
        expiration_date = request.POST.get('expiration_date')

        item = get_object_or_404(Item, id=item_id)

        add_stock_lot(
            item=item,
            position=position,
            quantity=quantity,
            lot=lot,
            expiration_date=expiration_date,
            user=request.user
        )

        messages.success(request, 'Lote adicionado com sucesso')
        return redirect('storage:position_detail', position_id=position.id)

    return render(request, 'storage/pages/position_detail.html', {
        'position': position,
        'stocklots': stocklots,
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

        stock = StockLot.objects.filter(item=item, position=position).first()

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
def position_edit(request, position_id, lot_id):
    position = get_object_or_404(Position, id=position_id)
    stocklot = get_object_or_404(StockLot, id=lot_id, position=position)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity')

        with transaction.atomic():
            adjust_stock_lot(
                stocklot=stocklot,
                new_quantity=new_quantity,
                user=request.user
            )

        messages.success(request, 'Lote atualizado com sucesso')
        return redirect('storage:position_detail', position_id=position.id)

    return render(request, 'storage/pages/position_edit.html', {
        'position': position,
        'stocklot': stocklot
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
        movements = movements.filter(item__code=item)

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # paginação (depois dos filtros)
    paginator = Paginator(movements, 20)
    page = request.GET.get('page')
    movements = paginator.get_page(page)

    return render(request, "storage/pages/movement_history.html", {
        "movements": movements
    })

def consolidation_storage(request):

    # 📦 total por item
    items_summary = (
        StockLot.objects
        .values('item__id', 'item__code')
        .annotate(
            total_quantity=Sum('quantity'),
            total_positions=Count('position', distinct=True)
        )
        .order_by('item__code')
    )

    # 📍 posições ocupadas (DISTINCT é essencial agora)
    occupied_positions = (
        StockLot.objects
        .filter(quantity__gt=0)
        .values('position')
        .distinct()
        .count()
    )

    # 📍 total de posições
    total_positions = Position.objects.count()

    # 📍 posições vazias
    empty_positions = total_positions - occupied_positions

    context = {
        'items_summary': items_summary,
        'occupied_positions': occupied_positions,
        'empty_positions': empty_positions,
        'total_positions': total_positions
    }

    return render(request, 'storage/pages/stock_datas.html', context)