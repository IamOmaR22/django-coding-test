from django.views import generic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from product.models import Variant, Product
from django.shortcuts import redirect, render
from django.views import View


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

    def get(self, request, *args, **kwargs):
        # Fetch products from the database
        products = Product.objects.all()

        # Pass products to the template
        context = {'products': products}
        return render(request, self.template_name, context)