import redis

from collections.abc import Iterable, Collection

from django.conf import settings

from .models import Product


r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


class Recommender:
    def get_product_key(self, id) -> str:
        return f'product:{id}:purchased_with'

    def products_bought(self, products: Iterable[Product]) -> None:
        products_ids = [p.id for p in products]
        for product_id in products_ids:
            for with_id in products_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self,
                             products: Collection[Product],
                             max_result: int = 6
                             ) -> list[Product]:
        products_ids = [p.id for p in products]
        if len(products) == 1:
            suggestions = r.zrange(self.get_product_key(products_ids[0]), 0, -1, desc=True)[:max_result]
        else:
            flat_ids = ''.join((str(id) for id in products_ids))
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(id) for id in products_ids]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *products_ids)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_result]
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products
