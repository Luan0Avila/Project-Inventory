from django.db import models


class Position(models.Model):
    position = models.CharField(max_length=10, unique=True)
    occupied = models.BooleanField(default=False)

    def __str__(self):
        return self.position

class Item(models.Model):
    code = models.CharField(max_length=7, unique=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.code