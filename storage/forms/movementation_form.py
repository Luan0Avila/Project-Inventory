from django import forms
from django.db.models import Sum
from ..models import Item, Position, StockLot


class StockMovementForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all())
    quantity = forms.DecimalField(max_digits=10, decimal_places=2)

    from_position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        label='Posição de origem'
    )

    to_position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        label='Posição de destino'
    )

    def clean(self):
        cleaned_data = super().clean()

        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        from_position = cleaned_data.get('from_position')
        to_position = cleaned_data.get('to_position')

        if not from_position and not to_position:
            raise forms.ValidationError(
                'Informe uma posição de origem ou destino.'
            )

        if from_position and to_position and from_position == to_position:
            raise forms.ValidationError(
                'Origem e destino não podem ser iguais.'
            )

        # 🔥 validação nova (somando lotes)
        if from_position and item and quantity:
            total = (
                StockLot.objects
                .filter(item=item, position=from_position)
                .aggregate(total=Sum('quantity'))
            )['total'] or 0

            if total < quantity:
                raise forms.ValidationError(
                    f'Estoque insuficiente. Disponível: {total}'
                )

        return cleaned_data

class PositionAdjustForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all()) # alterar esse campo para ter uma forma de digitar e ter autocomplete
    quantity = forms.DecimalField(min_value=0)
