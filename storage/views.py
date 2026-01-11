from django.shortcuts import render, redirect
from .models import Stock, Position, Stock, Movement
from django.db.models import Exists, OuterRef
from django.contrib import messages
from django.db import transaction
from .forms import StockMovementForm

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
