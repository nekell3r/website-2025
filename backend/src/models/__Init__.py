import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.products import ProductsOrm
from src.models.purchases import PaymentOrm
from src.models.reviews import ReviewsOrm
from src.models.users import UsersOrm