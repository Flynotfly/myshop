from decimal import Decimal

from django.conf import settings

from coupons.models import Coupon
from shop.models import Product


class Cart:
    def __init__(self, request):
        """
        initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Mark session as modified.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def total_price(self) -> Decimal:
        return sum((Decimal(item['price']) * item['quantity'] for item in self.cart.values()), start=Decimal(0))

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        try:
            del self.session['coupon_id']
        except KeyError:
            pass
        self.save()

    @property
    def coupon(self) -> Coupon | None:
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    @property
    def discount(self) -> Decimal:
        if self.coupon:
            return self.coupon.discount / Decimal(100) * self.total_price
        return Decimal(0)

    @property
    def total_price_after_discount(self) -> Decimal:
        return self.total_price - self.discount
