from django.db import models


class Position(models.Model):
    position = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.position


class Item(models.Model):
    code = models.CharField(max_length=7, unique=True)
    description = models.CharField(max_length=100, default=None)

    def __str__(self):
        return self.code
    
class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('item', 'position')


    def __str__(self):
        return f"{self.item} - {self.position}"
    

class Movement(models.Model):
    IN = 'IN'
    OUT = 'OUT'

    MOVEMENT_TYPES = [
        (IN, 'Entrada'),
        (OUT, 'Saída'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} {self.movement_type} {self.quantity}"


class Transfer(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    from_position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='transfer_out'
    )
    to_position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='transfer_in'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.item} {self.from_position} → {self.to_position}'
