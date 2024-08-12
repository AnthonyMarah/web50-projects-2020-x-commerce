from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:listing_id>/add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('listing/<int:listing_id>/remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('listing/<int:listing_id>/close/', views.close_auction, name='close_auction'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/<int:category_id>/', views.category_listings, name='category_listings'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
]
