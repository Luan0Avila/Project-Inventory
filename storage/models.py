from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    position = models.CharField(max_length=10, unique=True) # avaliar necessidade de alteração, pois pode haver mais de um item em uma posição

    def __str__(self):
        return self.position


class Item(models.Model):
    code = models.CharField(max_length=7, unique=True)
    description = models.CharField(max_length=100, default=None)

    def __str__(self):
        return self.code
    
class StockLot(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)

    lot = models.CharField(max_length=50)
    expiration_date = models.DateField()

    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('item', 'position', 'lot', 'expiration_date')

    def __str__(self):
        return f"{self.item} | {self.position} | Lote: {self.lot}"

class StockMovement(models.Model):
    IN = 'IN'
    OUT = 'OUT'
    TRANSFER = 'TRANSFER'

    MOVEMENT_TYPES = [
        (IN, 'Entrada'),
        (OUT, 'Saída'),
        (TRANSFER, 'Transferência'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    from_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_from'
    )

    to_position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_to'
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} - {self.movement_type} - {self.quantity}"
