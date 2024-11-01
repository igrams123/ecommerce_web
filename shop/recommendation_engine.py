from .models import Sneaker, Order, Recommendation
from collections import Counter

def generate_recommendations(user):
    # Fetch orders associated with the user
    orders = Order.objects.filter(user=user)

    # Get the sneakers from those orders
    sneaker_counts = Counter([order.sneaker for order in orders])

    # Get the most common sneakers
    most_common_sneakers = sneaker_counts.most_common(3)
    recommended_sneakers = [sneaker for sneaker, count in most_common_sneakers]

    # Iterate through recommended sneakers and create a recommendation for each
    for sneaker in recommended_sneakers:
        recommendation, created = Recommendation.objects.get_or_create(user=user, sneaker=sneaker)
        recommendation.score = sneaker_counts[sneaker]  # Assuming you want to set the score based on the count
        recommendation.save()  # Save the recommendation
