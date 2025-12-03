from .product_tables import ProductTablesMixin
from .product_filters import ProductFiltersMixin
from .product_actions import ProductActionsMixin
from .product_toast import ProductToastMixin
from .product_utils import ProductUtilsMixin


class ProductsMixin(
    ProductTablesMixin,
    ProductFiltersMixin,
    ProductActionsMixin,
    ProductToastMixin,
    ProductUtilsMixin
):

    pass
