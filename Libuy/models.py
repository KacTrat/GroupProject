from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Auction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags, blank=True)
    date_start = models.DateTimeField(default=timezone.now)
    date_end = models.DateTimeField()
    price_start = models.DecimalField(max_digits=7, decimal_places=2)
    current_price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.price_start <= 0:
            raise ValidationError("Starting price must be bigger than zero.")
        if self.date_end <= self.date_start:
            raise ValidationError("The auction end date must be after the start date.")

    def __str__(self):
        return f"Auction for {self.book.title} by {self.owner.username}"

    def save(self, *args, **kwargs):
        if self.current_price == 0.00:
            self.current_price = self.price_start
        super().save(*args, **kwargs)

class Bid(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-value']

    def clean(self):
        if not self.auction.is_active:
            raise ValidationError("The auction has ended.")
        if self.value <= self.auction.current_price:
            raise ValidationError("Your bid must be higher than the current price.")

    def save(self, *args, **kwargs):
        self.clean()
        self.auction.current_price = self.value
        self.auction.save(update_fields=['current_price'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bid of {self.value} by {self.owner.username} on auction {self.auction.book.title}"