from django.urls import path
from .views import (
    register,
    add_sneaker,
    sneaker_list,
    sneaker_detail,
    add_to_cart,
    cart,
    update_cart_quantity,
    remove_from_cart,
    checkout,  # Ensure this matches the function name
    order_confirmation,
    add_review,
    add_recommendation,
    saved_sneakers,
    save_sneaker,
    remove_saved_sneaker,
    initiate_payment,
    mpesa_callback,
    sneaker_search,
    user_login,
     user_logout
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('add-sneaker/', add_sneaker, name='add_sneaker'),
    path('sneakers/', sneaker_list, name='sneaker_list'),
    path('sneaker/<int:pk>/', sneaker_detail, name='sneaker_detail'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('update-cart/<int:cart_item_id>/<str:action>/', update_cart_quantity, name='update_cart_quantity'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),  # Ensure this matches the function name
    path('order-confirmation/', order_confirmation, name='order_confirmation'),
    path('add-review/<int:pk>/', add_review, name='add_review'),
    path('add-recommendation/<int:sneaker_id>/', add_recommendation, name='add_recommendation'),
    path('saved-sneakers/', saved_sneakers, name='saved_sneakers'),
    path('save-sneaker/<int:pk>/', save_sneaker, name='save_sneaker'),
    path('remove-saved-sneaker/<int:pk>/', remove_saved_sneaker, name='remove_saved_sneaker'),
    path('initiate_payment/', initiate_payment, name='initiate_payment'),
    path('mpesa_callback/', mpesa_callback, name='mpesa_callback'),
    path('search/', sneaker_search, name='sneaker_search'),

]