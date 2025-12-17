"""
Documents Router
API для генерации и скачивания PDF документов
"""

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import Response
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.pdf_generator import pdf_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents/ride/{ride_id}/receipt")
async def get_ride_receipt(
    request: Request,
    ride_id: int,
    download: bool = Query(False, description="Скачать файл вместо отображения")
):
    """
    Генерация квитанции поездки в PDF.
    
    - **ride_id**: ID поездки
    - **download**: Если true - скачивает файл, иначе открывает в браузере
    """
    
    # TODO: Получить данные поездки из БД
    # ride = await ride_crud.get_by_id(request.state.session, ride_id)
    # if not ride:
    #     raise HTTPException(status_code=404, detail="Ride not found")
    
    # Пока используем тестовые данные
    try:
        pdf_bytes = await pdf_generator.generate_ride_receipt(
            ride_id=ride_id,
            client_name="Иван Иванов",  # TODO: из БД
            driver_name="Пётр Петров",  # TODO: из БД
            pickup_address="Москва, ул. Ленина 1",  # TODO: из БД
            dropoff_address="Москва, ул. Пушкина 10",  # TODO: из БД
            fare=500.00,  # TODO: из БД
            distance_km=12.5,
            duration_min=25,
            payment_method="Наличные"
        )
    except Exception as e:
        logger.error(f"Failed to generate receipt PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    headers = {}
    if download:
        headers["Content-Disposition"] = f"attachment; filename=receipt_{ride_id}.pdf"
    else:
        headers["Content-Disposition"] = f"inline; filename=receipt_{ride_id}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers
    )


@router.get("/documents/driver/{driver_id}/report")
async def get_driver_report(
    request: Request,
    driver_id: int,
    period_days: int = Query(30, ge=1, le=365, description="Период отчёта в днях"),
    download: bool = Query(False)
):
    """
    Генерация отчёта водителя за период.
    
    - **driver_id**: ID профиля водителя
    - **period_days**: Период отчёта в днях (по умолчанию 30)
    - **download**: Скачать файл
    """
    
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)
    
    # TODO: Получить данные из БД
    # driver = await driver_profile_crud.get_by_id(request.state.session, driver_id)
    # rides = await ride_crud.get_by_driver_and_period(...)
    
    # Тестовые данные
    test_rides = [
        {"id": 101, "date": "15.12.2025", "route": "Ленина → Пушкина", "fare": 350.00},
        {"id": 102, "date": "16.12.2025", "route": "Гагарина → Мира", "fare": 520.00},
        {"id": 103, "date": "17.12.2025", "route": "Центр → Аэропорт", "fare": 1200.00},
    ]
    
    try:
        pdf_bytes = await pdf_generator.generate_driver_report(
            driver_name="Пётр Петров",  # TODO: из БД
            period_start=period_start,
            period_end=period_end,
            rides=test_rides,
            total_earnings=2070.00,
            total_commission=310.50
        )
    except Exception as e:
        logger.error(f"Failed to generate driver report PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    headers = {}
    filename = f"driver_report_{driver_id}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.pdf"
    if download:
        headers["Content-Disposition"] = f"attachment; filename={filename}"
    else:
        headers["Content-Disposition"] = f"inline; filename={filename}"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers
    )


@router.get("/documents/user/{user_id}/balance")
async def get_balance_statement(
    request: Request,
    user_id: int,
    download: bool = Query(False)
):
    """
    Генерация выписки по балансу пользователя.
    
    - **user_id**: ID пользователя
    - **download**: Скачать файл
    """
    
    # TODO: Получить данные из БД
    # user = await user_crud.get_by_id(request.state.session, user_id)
    # transactions = await transaction_crud.get_by_user(...)
    
    # Тестовые данные
    test_transactions = [
        {"id": 1, "date": "10.12.2025", "is_withdraw": False, "amount": 1000.00},
        {"id": 2, "date": "12.12.2025", "is_withdraw": True, "amount": 350.00},
        {"id": 3, "date": "15.12.2025", "is_withdraw": False, "amount": 500.00},
        {"id": 4, "date": "17.12.2025", "is_withdraw": True, "amount": 520.00},
    ]
    
    try:
        pdf_bytes = await pdf_generator.generate_balance_statement(
            user_name="Иван Иванов",  # TODO: из БД
            current_balance=630.00,  # TODO: из БД
            transactions=test_transactions
        )
    except Exception as e:
        logger.error(f"Failed to generate balance statement PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    headers = {}
    filename = f"balance_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    if download:
        headers["Content-Disposition"] = f"attachment; filename={filename}"
    else:
        headers["Content-Disposition"] = f"inline; filename={filename}"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers
    )


@router.get("/documents/health")
async def documents_health():
    """Проверка доступности сервиса генерации PDF"""
    return {
        "status": "ok",
        "weasyprint_available": pdf_generator.weasyprint_available,
        "reportlab_available": pdf_generator.reportlab_available
    }


# Создание роутера для экспорта
documents_router = router
