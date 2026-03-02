from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from config.settings import STRIPE_SECRET_KEY
from shop.models import *

from shop.forms import SignUpForm, SignInForm
import stripe

# Create your views here.
def index(request):
    slider=Slider.objects.all()
    banner=Banner.objects.all()
    product=Product.objects.all()
    categories = Category.objects.all()
    context={
        "sliders":slider,
        "banners":banner,
        "products":product,
        "categories":categories
    }
    return render(request,"shop/index.html",context)

def signup(request):
    form = SignUpForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            return redirect("signin")
    context = {
        "form":form
    }
    return render(request, "shop/signup.html",context)

def signin(request):
    form = SignInForm(data=request.POST or None)
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("home")
    context = {
        "form":form
    }
    return render(request, "shop/signin.html", context)

def signout(request):
    logout(request)
    return redirect("signin")

def category(request,pk):
    categories = Category.objects.all()
    cat=get_object_or_404(Category, pk=pk)
    products=Product.objects.filter(category=cat)
    sort_fields=request.GET.get('sort')
    price_fields=request.GET.getlist('price')
    color_fields = request.GET.getlist('color')
    size_fields=request.GET.getlist('size')
    if sort_fields:
        products=products.annotate(price=Min("types__price")).order_by(sort_fields).distinct()
    if color_fields:
        products=products.filter(types__color__in=color_fields).distinct()
    if size_fields:
        products=products.filter(types__size__in=size_fields).distinct()
    if price_fields:
        price_list={
            "10-100":(10,100),
            "100-200":(100,200),
            "200-300":(200,300),
            "300-400":(300,400),
            "400-500":(400,500),
        }
        query=Q()
        for key in price_fields:
            if key in price_list:
                low,high=price_list[key]
                query |=Q(types__price__gte=low,types__price__lte=high)
        if query:
            products=products.filter(query).distinct()
    paginator=Paginator(products,3)
    page_number=request.GET.get('page')
    obj_list=paginator.get_page(page_number)
    context = {
    "categories":categories,
    "products":obj_list,
    "current_category": cat,
    "selected_prices": price_fields,
    "color_fields":color_fields
    }
    return render(request, "shop/category.html", context)

def product_detail(request, pk):
    product = get_object_or_404(Product,pk=pk)
    if request.method == "POST":
        if request.user.is_authenticated:
            text = request.POST.get("text")
            Comment.objects.create(product=product, user=request.user, text=text)
            return redirect("product_detail",pk=pk)
    comments = product.comments.all().order_by("-created_at")
    context={
        "product": product,
        "comments":comments
    }
    return render(request, "shop/detail.html", context)


@login_required
def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        Contact.objects.create(full_name=full_name,email=email,message=message)
    return render(request, "shop/contact.html")

def search(request):
    word=request.GET.get("q")
    product=Product.objects.filter(Q(title__icontains=word))
    context={
        "products":product
    }
    return render(request,"shop/search.html",context)
@login_required
def likes(request):
    user=request.user if request.user.is_authenticated else None
    likes=Likes.objects.filter(user=user)
    products=[like.product for like in likes]
    context={
        "products":products
    }
    return render(request,"shop/like.html",context)
@login_required
def like_add(request,pk):
    user=request.user if request.user.is_authenticated else None
    product=Product.objects.get(pk=pk)
    if product:
        liked_product=Likes.objects.filter(user=user)
        if product in [like.product for like in liked_product]:
            like_product=Likes.objects.filter(user=user,product=product)
            like_product.delete()
        else:
            Likes.objects.create(user=user,product=product)
    next_page=request.META.get("HTTP_REFERER","home")
    return redirect(next_page)

@login_required
def basket(request):
    user=request.user if request.user.is_authenticated else None
    products=Basket.objects.filter(user=user)
    total_price=sum([item.get_total_price() for item in products])
    total_sale=sum([item.get_total_sale() for item in products])
    benefit=total_price-total_sale
    total_quantity=sum([item.quantity for item in products])
    if request.method== "POST":
        stripe.api_key=STRIPE_SECRET_KEY
        session=stripe.checkout.Session.create(
            line_items=[
                {"price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Coza shop",
                    },
                    "unit_amount":int(total_sale)*100
                },
                "quantity":1
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("success")),
            cancel_url=request.build_absolute_uri(reverse("cancel"))
        )
        return redirect(session.url)

    context = {
        "products": products,
        "total_sale": total_sale,
        "total_price": total_price,
        "total_quantity": total_quantity,
        "benefit": benefit
    }

    return render(request,"shop/basket.html",context)

def success(request):
    return render(request,"shop/success.html")

def cancel(request):
    return render(request,"shop/cancel.html")

@login_required
def basket_add(request,pk):
    product=Product.objects.get(pk=pk)
    quantity=request.POST.get("quantity")
    if quantity:
        quantity=int(quantity)
    else:
        quantity=1
    basket_products,created=Basket.objects.get_or_create(product=product,user=request.user)
    if not created:
        basket_products.quantity+=quantity
        basket_products.save()
    else:
        basket_products.quantity=quantity
        basket_products.save()
    next_page=request.META.get("HTTP_REFERER","home")
    return redirect(next_page)

@login_required
def basket_update(request,pk):
    product=get_object_or_404(Basket,pk=pk,user=request.user)
    if request.method=="POST":
        action=request.POST.get("action")
        if action=="+":
            product.quantity+=1
        elif action=="-":
            if product.quantity>1:
                product.quantity-=1
            else:
                product.delete()
                return redirect("basket")
        product.save()
    return redirect("basket")

@login_required
def basket_delete(request,pk):
    product = get_object_or_404(Basket, pk=pk, user=request.user)
    product.delete()
    return redirect("basket")









