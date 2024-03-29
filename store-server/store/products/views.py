from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from common.views import TitleMixin
from products.models import Basket, Product

# Create your views here.


class IndexView(TitleMixin, TemplateView):
    template_name = 'products/index.html'
    title = 'Store'


class ProductListView(TitleMixin, ListView):
    model = Product
    template_name = 'products/products.html'
    title = 'Store - Каталог'
    paginate_by = 3

    def get_queryset(self):
        queryset = super(ProductListView, self).get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id) if category_id else queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data()
        categories = cache.get('categories')
        if not categories:
            context['categories'] = list(set(map(lambda p: p.category, Product.objects.all())))
            cache.set('categories', context['categories'], 30)
        else:
            context['categories'] = categories
        return context


# def products(request, category_id=None, page_number=1):
#
#     products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
#
#     categories = list(set(map(lambda p: p.category, Product.objects.all())))
#
#     per_page = 3
#     paginator = Paginator(products, per_page)
#     products_paginator = paginator.page(page_number)
#
#     context = {
#         'title': 'Store - Каталог',
#         'categories': categories,
#         'products': products_paginator,
#     }
#     return render(request, 'products/products.html', context)


@login_required
def basket_add(request, product_id):
    Basket.create_or_update(product_id, request.user)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])
