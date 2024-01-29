from django.views import generic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from product.models import Variant, Product
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
            # Extract data from the POST request
            product_name = request.POST.get('product_name')
            product_sku = request.POST.get('product_sku')
            description = request.POST.get('description')

            # For demonstration purposes, print the extracted data
            print(f"Product Name: {product_name}")
            print(f"Product SKU: {product_sku}")
            print(f"Description: {description}")

            # Now, you can save the extracted data to your database
            # Replace the following lines with your actual model and field names
            new_product = Product.objects.create(
                title=product_name,
                sku=product_sku,
                description=description
            )

            # Return a success message
            # return JsonResponse({'message': 'Product created successfully!'})
            return redirect('product:list.product')

        except Exception as e:
            # Print the actual error message
            print(f"Error creating product: {str(e)}")

            # Return an error message with a 500 status code
            return JsonResponse({'message': f'Error creating product: {str(e)}'}, status=500)


class ProductListView(View):
    template_name = 'products/list.html'
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        # Fetch products from the database
        products = Product.objects.all()

        # Pagination logic
        paginator = Paginator(products, self.paginate_by)
        page = request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If the page is not an integer, deliver the first page.
            products = paginator.page(1)
        except EmptyPage:
            # If the page is out of range, deliver the last page of results.
            products = paginator.page(paginator.num_pages)

        # Pass products to the template
        context = {'products': products}
        return render(request, self.template_name, context)
    

class EditProductView(View):
    template_name = 'products/create.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Fetch product and variants data for editing
        product_id = kwargs.get('id')
        product = get_object_or_404(Product, id=product_id)
        variants = Variant.objects.filter(active=True).values('id', 'title')

        # Render the edit form with pre-filled data
        return render(request, self.template_name, {'product': product, 'variants': variants})

    def post(self, request, *args, **kwargs):
        try:
            # Extract data from the POST request
            product_id = kwargs.get('id')
            product = get_object_or_404(Product, id=product_id)
            product.title = request.POST.get('product_name')
            product.sku = request.POST.get('product_sku')
            product.description = request.POST.get('description')
            product.save()

            # Process variants and values here (similar to CreateProductView)

            # Redirect to the product list page after successful edit
            return redirect('product:list.product')

        except Exception as e:
            # Print the actual error message
            print(f"Error editing product: {str(e)}")

            # Return an error message with a 500 status code
            return JsonResponse({'message': f'Error editing product: {str(e)}'}, status=500)