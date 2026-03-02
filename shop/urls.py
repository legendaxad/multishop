from django.urls import path

from shop.views import *

urlpatterns=[
    path("",index,name="home"),
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    path("search/", search, name="search"),
    path("likes/", likes, name="likes"),
    path("like/<int:pk>/", like_add, name="like_add"),
    path("basket/", basket, name="basket"),
    path("basket_add/<int:pk>/",basket_add, name="basket_add"),
    path("basket_delete/<int:pk>/", basket_delete, name="basket_delete"),
    path("basket_update/<int:pk>/", basket_update, name="basket_update"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("contact/", contact, name="contact"),
    path("categories/<int:pk>/", category, name="category"),
    path("product/<int:pk>/", product_detail, name="product_detail"),



]