from django.views.generic import TemplateView, View, ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.models import Group as userGroup
from .models import *
from .models import Group as ProdGroup
from .forms import SupplierForm, OrganizationForm, ProductForm, PriceForm
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Max
from django.utils import timezone
from decimal import Decimal
import datetime

import random

class Index(TemplateView):
    template_name = "index.html"
    
    
class SupplierFormView(View):
	form_class = SupplierForm
	template_name = "registration_supp_form.html"

	#display blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	#process form data
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():

			user = form.save(commit=False)

			#normalize data
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			# add user to correct group
			g = userGroup.objects.get(name='Suppliers') 
			g.user_set.add(user)

			# authenticate then login supplier

			user = authenticate(username = username,password = password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('supplier_products')

		return render(request, self.template_name, {'form': form})

class OrganizationFormView(View):
	form_class = OrganizationForm
	template_name = "registration_org_form.html"

	#display blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	#process form data
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():

			user = form.save(commit=False)

			#normalize data
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()


			# add user to correct group
			g = userGroup.objects.get(name='Organizations') 
			g.user_set.add(user)

			# authenticate then login supplier

			user = authenticate(username = username,password = password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('org_home')

		return render(request, self.template_name, {'form': form})


def create_prices(request, product_id):
	if not request.user.is_authenticated():
		return redirect('index')
	else:
		form = PriceForm(request.POST or None, request.FILES or None)
		product = Product.objects.get(item_code=product_id)
		
		if form.is_valid():
			prices = Price.objects.all()
			price = form.save(commit=False)
			price.price_id = prices.aggregate(Max('price_id'))['price_id__max'] + 1
			# price.supplier_id = request.user
			price.save()
			pp = Product_Price()
			pp.price_id = price
			pp.item_code = product
			pp.save()
			if request.POST.get('submit'):
				return redirect('supplier_products')
			else:
				return redirect('create_prices',product.item_code)

		context = {
			"form": form,
			"product": product
		}
		return render(request, 'create_prices.html', context)

def create_product(request):
	if not request.user.is_authenticated():
		return redirect('index')
	else:
		form = ProductForm(request.POST or None, request.FILES or None)

		if form.is_valid():
			product = form.save(commit=False)
			product.supplier_id = request.user
			product.save()
			# return redirect('supplier_products')
			return redirect('create_prices',product.item_code)

		context = {
			"form": form,
		}
		return render(request, 'create_product.html', context)

def delete_product(request, product_id):
	product = Product.objects.get(item_code=product_id)
	product.delete()
	return redirect('supplier_products')

def delete_price(request, price_id):
	product_price = Product_Price.objects.get(price_id=price_id)
	price = Price.objects.get(price_id=price_id)
	product = Product.objects.get(item_code=product_price.item_code_id)
	user = request.user
	price.delete()
	product_price.delete()
	return render(request, 'product_detail.html', {'product': product, 'user': user})

def update_product(request, product_id):
	instance = get_object_or_404(Product, item_code=product_id)
	form = ProductForm(request.POST or None, instance=instance)
	if form.is_valid():
		form.save()
		return redirect('supplier_products')
	return render(request, 'update_product.html', {'form': form})

def SuppLogin(request):

	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('supplier_products')
			else:
				return render(request, 'login_supp_form.html', {'error_message': 'Your account has been disabled'})
		else:
			return render(request, 'login_supp_form.html', {'error_message': 'Invalid login'})
	return render(request, 'login_supp_form.html')

def OrgLogin(request):

	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('org_home')
			else:
				return render(request, 'login_org_form.html', {'error_message': 'Your account has been disabled'})
		else:
			return render(request, 'login_org_form.html', {'error_message': 'Invalid login'})
	return render(request, 'login_org_form.html')

def logout_user(request):
    logout(request)
    if is_Supplier(request.user):
    	form = SupplierForm(request.POST or None)
    else:
    	form = OrganizationForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'index.html', context)

def supplier_products(request):
	if not request.user.is_authenticated():
		return render(request, 'index.html')
	else:
		products = Product.objects.filter(supplier_id=request.user)
		page = request.GET.get('page', 1)
		query = request.GET.get("q")
		paginator = Paginator(products, 24)

		if query:
			products = products.filter(
				Q(description__icontains=query) |
				Q(product_name__icontains=query)
			).distinct()
		else:
			try:
				products = paginator.page(page)
			except PageNotAnInteger:
				products = paginator.page(1)
			except EmptyPage:
				products = paginator.page(paginator.num_pages)
			return render(request, 'supplier_products.html', {'products': products})
		return render(request, 'supplier_products.html', {'products': products})


def SuppProductDetail(request, product_id):
    if not request.user.is_authenticated():
        return render(request, 'index')
    else:
        user = request.user
        product = get_object_or_404(Product, pk=product_id)
        return render(request, 'product_detail.html', {'product': product, 'user': user})


# home page and top picks - just a random sample - we can implement a better algorithm later
class OrgHome(TemplateView):
    template_name = "org_home.html"
    def get_context_data(self, **kwargs):
	context = super(OrgHome, self).get_context_data(**kwargs)
	context["products"] = random.sample(Product.objects.all(), 4)
	return context
    
# Main list of products - simple filtering for search and category selection
class OrgProducts(ListView):
    
    model = Product
    template_name = "org_products.html"
    paginate_by = 24 # I love django
    
    def get_context_data(self, **kwargs):
	context = super(OrgProducts, self).get_context_data(**kwargs)
	context['catgeories'] = Product.objects.order_by("category").values_list("category", flat = True).distinct()
	context['query'] = self.request.GET.get("q", "")
	context['category'] = self.request.GET.get("category", "")
	return context
    
    # Filtering and search
    def get_queryset(self):
	query = self.request.GET.get("q", None)
	category = self.request.GET.get("category", None)
	original = super(OrgProducts, self).get_queryset().order_by("created")
	if query:
		search = Search_Item(keyword= query,created=datetime.datetime.now(),org_id=self.request.user)
		search.save()
		return original.filter(product_name__icontains = query)
	elif category:
	    return original.filter(category = category)
	else:
	    return original
    
# Product detail pages - simple post for creating new groups
class OrgProductDetail(DetailView):
    template_name = "product_single.html"
    model = Product
    
    # The input needs to be cleaned before being used in a model creation
    def post(self, request, **kwargs):
	name = request.POST.get("name", None)
	pk = request.POST.get("product_pk", None)
	pledge_amt = request.POST.get("pledge",None)
	selected_price_id = request.POST.get("target",None)
	if not name or not pk or not pledge_amt or not selected_price_id: return redirect(request.get_full_path())

	price = get_object_or_404(Price, price_id=selected_price_id)
	payment = Payment(created = datetime.datetime.now(),cc_expiry = '111', cc_number = '111111111', cc_ccv = '123',amount = Decimal(pledge_amt)*price.price)
	payment.save()
	prod_price = Product_Price.objects.get(item_code = pk, price_id = price.price_id)
	g = ProdGroup(name = name, product_id = get_object_or_404(Product, pk = pk),product_price=prod_price)
	g.save()
	g.members.add(request.user)
	p = Pledge(group_id= g,payment_id=payment,org_id=request.user)
	p.save()
	return redirect(request.get_full_path())
    
    def get_context_data(self, **kwargs):
	context = super(OrgProductDetail, self).get_context_data(**kwargs)
	context["groups"] = self.object.group_set.filter(is_open = True)
	return context

class OrgGroupDetail(DetailView):
	model = ProdGroup
	template_name = "group_single.html"

	def post(self, request, **kwargs):
		pledge_amt = request.POST.get("pledge",None)
		pk = request.POST.get("group_pk",None)
		if not pledge_amt or not pk: return redirect(request.get_full_path())

		g = get_object_or_404(Group,group_id=pk)
		payment = Payment(created = datetime.datetime.now(),cc_expiry = '111', cc_number = '111111111', cc_ccv = '123',amount = Decimal(pledge_amt))
		payment.save()
		p = Pledge(group_id= g,payment_id=payment,org_id=request.user)
		p.save()
		return redirect(request.get_full_path())

	def get_context_data(self, **kwargs):
		context = super(OrgGroupDetail, self).get_context_data(**kwargs)
		pledges = Pledge.objects.filter(group_id=self.object)
		allow_pledge = True
		if self.request.user in self.object.members.all():
			allow_pledge = False
		context["pledges"] = pledges
		context["allow_pledge"] = allow_pledge
		return context


'''********** HELPER FUNCTIONS ************ '''

def is_Supplier(user):
    return user.groups.filter(name='Suppliers').exists()

def is_Organization(user):
	return user.groups.filter(name='Organizations').exists()