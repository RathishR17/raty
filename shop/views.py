from django.shortcuts import render, redirect
from django.http import JsonResponse
from .form import CustomUserForm, CustomerProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
import razorpay
from django.views import View
from django.conf import settings
from .models import *


# Create your views here.
def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, "shop/index.html", {"products": products})


def favviewpage(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request, "shop/fav.html", {"fav": fav})
    else:
        return redirect("/")


def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")


def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, "shop/cart.html", {"cart": cart})
    else:
        return redirect("/")


def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")


class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=request.user)
        cart_item = Cart.objects.filter(user=request.user)
        famount = 0
        for p in cart_item:
            value = p.product_qty * p.product.selling_price
            famount = famount + value
        totalamount = famount
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        # {'id':'order_KU0n5eKcEeiLOm', 'entity': 'order', 'amount': 14500, 'amount_paid': 0, 'amount_due 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts'notes': [], 'created_at': 1665829122}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request,'checkout.html', locals())


def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    # print("payment_done : oid = ",order_id," pid ",payment_id," cid = ",cust_id)
    user = request.user
    # return redirect("orders")
    customer = Customer.objects.get(id=cust_id)
    # To update payment status and payment id
    payment = Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    # To save order details
    cart = Cart.objects.filter(user=request.user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, product_qty=c.product_qty, payment=payment).save()
        c.delete()
    return redirect("orders")


class orders(View):
    def get(self, request):
        order_placed = OrderPlaced.objects.filter(user=request.user)
        return render(request, 'orders.html', locals())


def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['pid']
            # print(request.user.id)
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out Successfully")
    return redirect("/")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request, username=name, password=pwd)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect("/")
    return render(request, "shop/login.html")


def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Success You can Login Now..!")
            return redirect('/login')
    return render(request, "shop/register.html", {"form": form})


def collections(request):
    Cate = category.objects.filter(status=0)
    return render(request, "shop/collections.html", {"Cate": Cate})


def collectionsview(request, name):
    if (category.objects.filter(name=name, status=0)):
        products = Product.objects.filter(category__name=name)
        return render(request, "shop/products/index.html", {"products": products, "category_name": name})
    else:
        messages.warning(request, "No such Category Found")
        return redirect('collections')


def product_details(request, cname, pname):
    if (category.objects.filter(name=cname, status=0)):
        if (Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, "shop/products/product_details.html", {"products": products})
        else:
            messages.error(request, "No Such Product Found")
            return redirect('collections')
    else:
        messages.error(request, "No Such Category Found")
        return redirect('collections')


class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user, name=name, locality=locality, city=city, mobile=mobile, state=state,
                           zipcode=zipcode)
            reg.save()
            messages.success(request, "Profile Saved Successfully")
        else:
            messages.warning(request, "Data Invalid")

        return render(request, 'profile.html', locals())


def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'address.html', locals())


class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'updateAddress.html', locals())

    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Profile Updated Successfully")
        else:
            messages.warning(request, "Data Invalid")


        return redirect('address')



