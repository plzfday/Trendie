from django.db import models


class Company(models.Model):
    ticker = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.ticker


class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=40)
    ticker_id = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ticker_id.ticker} - {self.keyword}"
