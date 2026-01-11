from django import forms
from ..models import Movement, Stock

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['item', 'position', 'movement_type', 'quantity']

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        position = cleaned_data.get('position')
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')

        if not all([item, position, movement_type, quantity]):
            return cleaned_data

        if movement_type == 'OUT':
            stock = Stock.objects.filter(
                item=item,
                position=position
            ).first()

            if not stock or stock.quantity < quantity:
                raise forms.ValidationError(
                    'Quantidade insuficiente em estoque para essa posição.'
                )

        return cleaned_data
