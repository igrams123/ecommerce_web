from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,authenticate
from .models import Sneaker, Order, Review, Recommendation, Saved, Cart, OrderItem
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient  # Importing MpesaClient
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import logout
import logging
from django.contrib import messages

# Registration view
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('sneaker_list')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

# Login view
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('sneaker_list')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {'form': form})

# Logout view
def user_logout(request):
    logout(request)
    return render(request, 'register/logged_out.html')

# View to add a sneaker
@login_required
def add_sneaker(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        category = request.POST.get('category')
        gender = request.POST.get('gender')

        sneaker = Sneaker.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            category=category,
            gender=gender
        )
        
        # Debugging output
        print(f"Added sneaker: {sneaker.name}, Category: {sneaker.category}, Image: {sneaker.image.url}")
        
        return redirect('sneaker_list')

    return render(request, 'shop/add_sneaker.html')
# View to list all sneakers categorized by sections
def sneaker_list(request):
    sneaker_sections = {
        'Trending': Sneaker.objects.filter(category='trending'),  # Key matches the template
        'New Arrivals': Sneaker.objects.filter(category='new_arrivals'),  # Key matches the template
        'Discounted': Sneaker.objects.filter(category='discounted'),  # Changed to match the template
        'Running': Sneaker.objects.filter(category='running'),
        'Lifestyle': Sneaker.objects.filter(category='lifestyle'),
        'Basketball': Sneaker.objects.filter(category='basketball'),
        'Outdoor': Sneaker.objects.filter(category='outdoor'),
    }
    context = {'sneaker_sections': sneaker_sections}
    return render(request, 'shop/sneaker_list.html', context)

# View to display sneaker details
def sneaker_detail(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    reviews = Review.objects.filter(sneaker=sneaker)
    recommendations = Recommendation.objects.filter(sneaker=sneaker)
    saved_items = Saved.objects.filter(sneaker=sneaker, user=request.user)
    return render(request, 'shop/sneaker_detail.html', {
        'sneaker': sneaker,
        'reviews': reviews,
        'recommendations': recommendations,
        'saved_items': saved_items
    })

# View to add a sneaker to the cart
@login_required
def add_to_cart(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    cart_item, created = Cart.objects.get_or_create(user=request.user, sneaker=sneaker)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

# View to display the cart
@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.sneaker.price * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# View to update cart item quantity
@login_required
def update_cart_quantity(request, cart_item_id, action):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('cart')

# View to remove an item from the cart
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# View to handle checkout with M-Pesa
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.sneaker.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Check if all required fields are filled
        if not name or not address or not phone:
            return render(request, 'shop/checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'error': "All fields are required."  # Set error message
            })

        # Initiate the M-Pesa payment
        mpesa_response = process_mpesa_payment(float(total_price), phone)

        # Handle the M-Pesa response
        if mpesa_response.get("ResponseCode") == "0":  # Assuming "0" indicates success
            # Create the order only if payment initiation is successful
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                name=name,
                address=address,
                phone=phone
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    sneaker=item.sneaker,
                    quantity=item.quantity
                )

            # Clear the cart after successful order
            cart_items.delete()

            return redirect('order_confirmation')  # Redirect to order confirmation page
        else:
            return render(request, 'shop/checkout.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'error': mpesa_response.get("errorMessage", "Payment initiation failed.")
            })

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
def process_mpesa_payment(amount, phone_number):
    # Create an instance of MpesaClient
    mpesa_client = MpesaClient()

    # Prepare the payment request
    response = mpesa_client.stk_push(
        amount=int(amount),  # Convert amount to integer
        phone_number=phone_number,
        callback_url='https://api.darajambili.com/express-payment',  # Use Darajambili's callback URL
        account_reference='SneakerShop',  # Change as needed
        transaction_desc='Payment for sneakers'  # Change as needed
    )

    return response  # Return the M-Pesa response

# View to display order confirmation
@login_required
def order_confirmation(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_confirmation.html', {'orders': orders})

# View to add a review for a sneaker
@login_required
def add_review(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            sneaker=sneaker,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect('sneaker_detail', pk=sneaker.pk)

    return render(request, 'shop/add_review.html', {'sneaker': sneaker})

# View to save a sneaker to the saved items
@login_required
def saved_sneakers(request):
    saved_sneakers = Saved.objects.filter(user=request.user)
    return render(request, 'shop/saved_sneakers.html', {'saved_sneakers': saved_sneakers})

@login_required
def save_sneaker(request, pk):
    sneaker = get_object_or_404(Sneaker, pk=pk)
    Saved.objects.get_or_create(user=request.user, sneaker=sneaker)
    return redirect('sneaker_detail', pk=sneaker.pk)  # Redirect after saving

# View to remove a sneaker from saved items
@login_required
def remove_saved_sneaker(request, pk):
    saved_item = get_object_or_404(Saved, pk=pk)
    saved_item.delete()
    return redirect('saved_sneakers')

# View to add a recommendation for a sneaker
@login_required
def add_recommendation(request, sneaker_id):
    sneaker = get_object_or_404(Sneaker, id=sneaker_id)
    if request.method == 'POST':
        score = request.POST.get('score')
        if score:
            try:
                score = int(score)
                Recommendation.objects.create(
                    user=request.user,
                    sneaker=sneaker,
                    score=score
                )
            except ValueError:
                pass
            return redirect('sneaker_detail', pk=sneaker_id)
    return redirect('sneaker_detail', pk=sneaker_id)

# Configure logging
logger = logging.getLogger(__name__)

@require_POST
def initiate_payment(request):
    amount = request.POST.get('amount')
    phone = request.POST.get('phone')
    name = request.POST.get('name')
    address = request.POST.get('address')
    
    # Check if all required fields are filled
    if not amount or not phone or not name or not address:
        return JsonResponse({'error': 'All fields are required.'}, status=400)

    try:
        # Call your M-Pesa processing function here
        mpesa_response = process_mpesa_payment(int(amount), phone)

        # Log the response for debugging
        logger.info(f'M-Pesa Response: {mpesa_response}')

        # Check the response attributes
        if hasattr(mpesa_response, 'ResponseCode') and mpesa_response.ResponseCode == "0":
            return JsonResponse({'success': True})
        else:
            # Log the error for debugging
            logger.error(f'M-Pesa error: {mpesa_response.errorMessage if hasattr(mpesa_response, "errorMessage") else "Unknown error"}')
            return JsonResponse({'error': 'Payment initiation failed. Please try again.'}, status=400)

    except Exception as e:
        # Log the exception for debugging
        logger.exception('Error during payment processing: %s', e)  # Log the full exception
        return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)

@csrf_exempt  # To allow M-Pesa to send requests without CSRF token
def mpesa_callback(request):
    if request.method == 'POST':
        # Parse the incoming JSON data from M-Pesa
        data = json.loads(request.body)

        # Extract necessary information
        transaction_id = data.get('transactionId')
        response_code = data.get('ResponseCode')
        amount = data.get('Amount')
        phone_number = data.get('phoneNumber')

        # Handle the response based on response code
        if response_code == "0":  # Assuming "0" indicates success
            # Update order status in your database
            # e.g., mark the order as paid
            # Order.objects.filter(transaction_id=transaction_id).update(status='paid')
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failure', 'message': 'Payment failed'}, status=400)

    return JsonResponse({'status': 'invalid_request'}, status=400)

def sneaker_search(request):
    query = request.GET.get('q')
    sneakers = Sneaker.objects.filter(name__icontains=query) if query else []
    context = {'sneakers': sneakers, 'query': query}
    return render(request, 'shop/sneaker_search_results.html', context)