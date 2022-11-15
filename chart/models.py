from django.db import models


class Ticker(models.Model):
    ticker = models.CharField(max_length=9)
    keyword = models.CharField(max_length=40)

    def __str__(self):
        return self.ticker
