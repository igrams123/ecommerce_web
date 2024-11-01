from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Sneaker(models.Model):
    CATEGORY_CHOICES = [
        ('trending', 'Trending'),
        ('new_arrivals', 'New Arrivals'),
        ('discounted', 'Discounted'),
        ('running', 'Running'),
        ('lifestyle', 'Lifestyle'),
        ('basketball', 'Basketball'),
        ('outdoor', 'Outdoor'),
    ]
    
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=100)
    address = models.TextField(default="N/A")  # Set a default value
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now)
    ordered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='Pending')  

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.sneaker.name} in Order {self.order.id}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s cart item: {self.sneaker.name} (Qty: {self.quantity})"

    @property
    def total_price(self):
        return self.sneaker.price * self.quantity

class Review(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.sneaker.name}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)  # Single sneaker relationship
    score = models.IntegerField()  # Score field added for recommendation ranking

    def __str__(self):
        return f"Recommendation for {self.user.username}"

class Saved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} saved {self.sneaker.name}"
