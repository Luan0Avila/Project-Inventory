from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock, Position, Stock, Movement, Item
from django.db.models import Exists, OuterRef
from django.contrib import messages
from django.db import transaction
from .forms import StockMovementForm
from .forms import PositionAdjustForm

def home(request):
    return render(request, 'storage/pages/home.html')

def storage_map(request):
    positions = Position.objects.annotate(
        occupied=Exists(
            Stock.objects.filter(
                position=OuterRef('pk'),
                quantity__gt=0
            )
        )
    )

    return render(request, 'storage/pages/map.html', {
        'positions': positions
    }) 



def stock_movement(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['item']
            quantity = form.cleaned_data['quantity']
            from_position = form.cleaned_data['from_position']
            to_position = form.cleaned_data['to_position']

            with transaction.atomic():

                # 🔁 SAÍDA
                if from_position:
                    Movement.objects.create(
                        item=item,
                        position=from_position,
                        movement_type='OUT',
                        quantity=quantity
                    )

                    stock_from = Stock.objects.get(
                        item=item,
                        position=from_position
                    )
                    stock_from.quantity -= quantity
                    stock_from.save()

                # 🔁 ENTRADA
                if to_position:
                    Movement.objects.create(
                        item=item,
                        position=to_position,
                        movement_type='IN',
                        quantity=quantity
                    )

                    stock_to, _ = Stock.objects.get_or_create(
                        item=item,
                        position=to_position,
                        defaults={'quantity': 0}
                    )
                    stock_to.quantity += quantity
                    stock_to.save()

            messages.success(request, 'Movimentação realizada com sucesso!')
            return redirect('storage:stock_movement')
    else:
        form = StockMovementForm()

    return render(request, 'storage/pages/movement_form.html', {
        'form': form
    })



def stock_overview(request):
    edit_id = request.GET.get('edit')

    if request.method == 'POST':
        position_id = request.POST.get('position_id')
        item_id = request.POST.get('item')
        new_quantity = float(request.POST.get('quantity'))

        position = Position.objects.get(id=position_id)
        item = Item.objects.get(id=item_id)

        stock = Stock.objects.filter(position=position).first()

        with transaction.atomic():
            if stock:
                diff = new_quantity - float(stock.quantity)

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

                stock.item = item
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

        messages.success(request, 'Estoque atualizado')
        return redirect('storage:stock_overview')

    positions = Position.objects.all()
    items = Item.objects.all()

    rows = []
    for position in positions:
        stock = Stock.objects.filter(position=position).select_related('item').first()

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

    return render(request, 'storage/pages/stock_overview.html', {
        'rows': rows,
        'items': items,
        'editing_position_id': int(edit_id) if edit_id else None
    })


def position_edit(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    stock = Stock.objects.filter(position=position).first()

    if request.method == 'POST':
        form = PositionAdjustForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['item']
            new_quantity = form.cleaned_data['quantity']

            with transaction.atomic():
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