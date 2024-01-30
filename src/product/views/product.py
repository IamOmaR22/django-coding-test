from django.views import generic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            product_name = self.request.POST.get('product_name')
            product_sku = self.request.POST.get('product_sku')
            description = self.request.POST.get('description')

            new_product = Product.objects.create(
                title=product_name,
                sku=product_sku,
                description=description
            )

            for variant in self.request.POST:
                if variant.startswith('variant_'):
                    variant_id = variant.split('_')[1]
                    variant_value = self.request.POST.get(variant)

                    product_variant = ProductVariant.objects.create(
                        product=new_product,
                        variant_title=variant_value,
                        variant_id=variant_id
                    )

                    # Check if price and stock values are provided
                    price = self.request.POST.get(f'price_{variant_id}')
                    stock = self.request.POST.get(f'stock_{variant_id}')

                    if price is not None and stock is not None:
                        ProductVariantPrice.objects.create(
                            product_variant_one=product_variant,
                            price=float(price),
                            stock=float(stock),
                            product=new_product
                        )

            return redirect('product:list.product')

        except Exception as e:
            return JsonResponse({'message': f'Error creating product: {str(e)}'}, status=500)




class ProductListView(View):
    template_name = 'products/list.html'
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.all()

            variants = Variant.objects.filter(active=True).values('id', 'title')

            title = request.GET.get('title')
            variant_id = request.GET.get('variant')
            price_from = request.GET.get('price_from')
            price_to = request.GET.get('price_to')
            date = request.GET.get('date')

            if title:
                products = products.filter(title__icontains=title)

            if variant_id:
                products = products.filter(productvariant_set__variant_id=variant_id)

            if price_from and price_to:
                products = products.filter(
                    productvariant_set__productvariantprice_set__price__range=(price_from, price_to)
                )

            if date:
                products = products.filter(created_at__date=date)

            paginator = Paginator(products, self.paginate_by)
            page = request.GET.get('page')

            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)

            context = {'products': products, 'variants': variants}
            
            # Include product variant prices in the context
            context['product_variant_prices'] = ProductVariantPrice.objects.all()

            return render(request, self.template_name, context)

        except Exception as e:
            return JsonResponse({'message': f'Error fetching products: {str(e)}'}, status=500)
    

class EditProductView(View):
    template_name = 'products/create.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        product = get_object_or_404(Product, id=product_id)
        # variants = Variant.objects.filter(active=True).values('id', 'title')
        existing_variants = product.productvariant_set.all()

        variants = Variant.objects.filter(active=True).values('id', 'title')

        return render(request, self.template_name, {'product': product, 'variants': variants, 'existing_variants': existing_variants})

    def post(self, request, *args, **kwargs):
        try:
            product_id = kwargs.get('id')
            product = get_object_or_404(Product, id=product_id)
            product.title = request.POST.get('product_name')
            product.sku = request.POST.get('product_sku')
            product.description = request.POST.get('description')
            product.save()

            return redirect('product:list.product')

        except Exception as e:
            print(f"Error editing product: {str(e)}")
            return JsonResponse({'message': f'Error editing product: {str(e)}'}, status=500)