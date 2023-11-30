import io

import product
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from shop.models import Product






# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))

    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request))
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()

    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()
    return redirect('cart:cart_detail')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity

    except ObjectDoesNotExist:
        pass

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter))


# for cart Item remove function :-

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')


# complete item deletion

def full_remove(request,product_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)

        cart_item.delete()
        return redirect('cart:cart_detail')

    except (Cart.DoesNotExist, Product.DoesNotExist, CartItem.DoesNotExist):
    # Handle the exception, e.g., redirect to the cart detail page with a message
        return redirect('cart:cart_detail')





# for printout



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# Your other imports...

def generate_report(request):
    template_path = 'print.html'

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
    except ObjectDoesNotExist:
        cart_items = []

    context = {'cart_items': cart_items}

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    # Render the template to HTML
    template = get_template(template_path)
    html = template.render(context)

    # Create PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Return the response
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response
