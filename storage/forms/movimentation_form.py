from django import forms
from ..models import Item, Position, Stock

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

        # ❌ ambos vazios
        if not from_position and not to_position:
            raise forms.ValidationError(
                'Informe uma posição de origem ou destino.'
            )

        # ❌ iguais
        if from_position and to_position and from_position == to_position:
            raise forms.ValidationError(
                'Origem e destino não podem ser iguais.'
            )

        # ❌ valida saída
        if from_position:
            stock = Stock.objects.filter(
                item=item,
                position=from_position
            ).first()

            if not stock or stock.quantity < quantity:
                raise forms.ValidationError(
                    'Quantidade insuficiente na posição de origem.'
                )

        return cleaned_data
