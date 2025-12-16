from fastapi import APIRouter, Query
from src.prices.service import PricesService

router = APIRouter()
price_service = PricesService()

@router.get("/necessities-price")
def get_prices(category: str = Query(None), commodity: str = Query(None)):
    return price_service.get_prices(category, commodity)
