from django.contrib import admin
from .models import Sneaker, Order, Review, Recommendation, Saved, OrderItem

class SneakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'gender')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'order_items', 'ordered_at')  # Display related OrderItem details

    def order_items(self, obj):
        items = OrderItem.objects.filter(order=obj)
        return ', '.join([f"{item.sneaker.name} (Qty: {item.quantity})" for item in items])

    order_items.short_description = 'Sneakers & Quantities'  # Add a short description for the admin panel

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('sneaker', 'user', 'rating', 'comment')

class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sneaker', 'score')  # Ensure 'sneaker' is correctly defined in your Recommendation model

class SavedAdmin(admin.ModelAdmin):
    list_display = ('user', 'sneaker')

admin.site.register(Sneaker, SneakerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Saved, SavedAdmin)
