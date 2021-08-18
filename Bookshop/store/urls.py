from django.urls import path

from . import views

urlpatterns = [path('', views.products_list),
               path("products/", views.products_list),
               path('products/product<int:product_id>/', views.products_detail),
               path("complaint/", views.complaint),
               path("complaint/<int:complaint_id>", views.complaint_details),
               path("products/<genre_name>/", views.genre_list),
               path("cart/", views.cart),
               path("cart/add/", views.add_to_cart),
               path("cart/remove_one/", views.remove_one_quantity_from_cart),
               path("cart/del/", views.del_from_cart),
               path("cart/clean/", views.clean_cart),
               path("order/", views.order),
               path("order/<int:order_id>", views.order_detail),
               path("payment_method/<int:order_id>", views.payment_method),
               path("payment/<int:payment_method_id>/<int:order_id>", views.payment, name='payment'),
               path("order/discount", views.add_discount_code),
               path("user_detail/", views.user_detail),
               path("search/", views.products_list_searched)
               ]
