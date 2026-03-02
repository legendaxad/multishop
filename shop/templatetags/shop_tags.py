from django import template
from ..models import Category, Likes, Basket

register = template.Library()



@register.simple_tag()
def get_likes(user):
    liked= Likes.objects.filter(user=user)
    return [like.product for like in liked]
@register.simple_tag()
def get_likes_count(user):
    liked= Likes.objects.filter(user=user)
    return len([like.product for like in liked])
@register.simple_tag()
def get_basket(user):
    basket= Basket.objects.filter(user=user)
    return [item.product for item in basket]
@register.simple_tag()
def get_basket_count(user):
    basket= Basket.objects.filter(user=user)
    return len([item.product for item in basket])

