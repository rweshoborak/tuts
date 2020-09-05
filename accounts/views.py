from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import OrderForms ,CreateUserForm,CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_users,admin_only


from django.http import HttpResponse


# Create your views here.

@unauthenticated_user
def registerUser(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form=CreateUserForm()
        if request.method=='POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                group = Group.objects.get(name='customer')
                user.groups.add(group)
                Customer.objects.create(
                    user=user,
                )

                messages.success(request,"You have successfully created a user " + username )

                return redirect('login')
        context = {
            'form':form
        }
        return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginUser(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username,password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
        else:
            messages.info(request,"Password or username is incorrect!!!!")
    context = {

    }
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context={
        'order':orders, 'delivered': delivered, 'pending': pending,
        'total_orders': total_orders,
    }

    return render(request,'accounts/user.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer =request.user.customer
    form= CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {
        'form':form
    }
    return render(request,'accounts/account_settings.html',context )



@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin'])
@admin_only
def home(request):
    customer = Customer.objects.all()
    orders = Order.objects.all()
    total_customers = customer.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'customer': customer, 'orders': orders, 'delivered': delivered, 'pending': pending,
        'total_customers': total_customers, 'total_orders': total_orders,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    product = Product.objects.all()
    context = {
        'product': product
    }
    return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        'customer': customer,
        'order':orders,
        'totalOrders':total_orders,
        'myFilter':myFilter,
    }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer,Order, fields=('product','status'), extra=2)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    #form = OrderForms(initial={'customer':customer})
    if request.method == 'POST':
        formset = OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {
        'formset':formset
    }
    return render(request,'accounts/orders_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    formset = OrderForms(instance=order)
    if request.method == 'POST':
        formset = OrderForms(request.POST, instance=order)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {
        'formset':formset,
    }

    return render(request,'accounts/orders_form.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method =='POST':
        order.delete()
        return  redirect('/')

    context ={
        'item':order
    }
    return render(request, 'accounts/delete_order.html', context)