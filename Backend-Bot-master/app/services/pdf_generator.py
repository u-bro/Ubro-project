"""
PDF Generator Service
Генерация PDF документов для квитанций, договоров, отчётов
"""

from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Попытка импорта weasyprint (может не быть установлен)
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not installed. PDF generation will use fallback method.")

# Fallback на reportlab если weasyprint недоступен
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed. PDF generation may be limited.")


class PDFGenerator:
    """
    Сервис генерации PDF документов.
    Поддерживает WeasyPrint (HTML → PDF) и ReportLab (программная генерация).
    """
    
    # CSS стили для PDF документов
    DEFAULT_CSS = """
        @page {
            size: A4;
            margin: 20mm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 24pt;
            font-weight: bold;
            color: #3498db;
        }
        .receipt-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .receipt-info p {
            margin: 5px 0;
        }
        .amount {
            font-size: 18pt;
            font-weight: bold;
            color: #27ae60;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background: #f2f2f2;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 10pt;
            color: #666;
        }
    """
    
    def __init__(self):
        self.weasyprint_available = WEASYPRINT_AVAILABLE
        self.reportlab_available = REPORTLAB_AVAILABLE
    
    async def generate_ride_receipt(
        self,
        ride_id: int,
        client_name: str,
        driver_name: str,
        pickup_address: str,
        dropoff_address: str,
        fare: float,
        distance_km: Optional[float] = None,
        duration_min: Optional[int] = None,
        payment_method: str = "Наличные",
        created_at: Optional[datetime] = None
    ) -> bytes:
        """Генерация квитанции поездки"""
        
        if created_at is None:
            created_at = datetime.utcnow()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Квитанция #{ride_id}</title>
        </head>
        <body>
            <div class="header">
                <div class="logo">🚗 U-BRO TAXI</div>
                <p>Квитанция об оплате поездки</p>
            </div>
            
            <h1>Квитанция #{ride_id}</h1>
            
            <div class="receipt-info">
                <p><strong>Дата:</strong> {created_at.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>Клиент:</strong> {client_name}</p>
                <p><strong>Водитель:</strong> {driver_name}</p>
            </div>
            
            <h2>Детали поездки</h2>
            <table>
                <tr>
                    <th>Параметр</th>
                    <th>Значение</th>
                </tr>
                <tr>
                    <td>Адрес подачи</td>
                    <td>{pickup_address}</td>
                </tr>
                <tr>
                    <td>Адрес назначения</td>
                    <td>{dropoff_address}</td>
                </tr>
                {f'<tr><td>Расстояние</td><td>{distance_km:.1f} км</td></tr>' if distance_km else ''}
                {f'<tr><td>Время в пути</td><td>{duration_min} мин</td></tr>' if duration_min else ''}
                <tr>
                    <td>Способ оплаты</td>
                    <td>{payment_method}</td>
                </tr>
            </table>
            
            <div class="receipt-info">
                <p><strong>Итого к оплате:</strong></p>
                <p class="amount">{fare:.2f} ₽</p>
            </div>
            
            <div class="footer">
                <p>Спасибо за использование U-BRO TAXI!</p>
                <p>Служба поддержки: support@u-bro.ru</p>
            </div>
        </body>
        </html>
        """
        
        return await self._generate_pdf_from_html(html)
    
    async def generate_driver_report(
        self,
        driver_name: str,
        period_start: datetime,
        period_end: datetime,
        rides: list,
        total_earnings: float,
        total_commission: float
    ) -> bytes:
        """Генерация отчёта водителя за период"""
        
        rides_rows = ""
        for ride in rides:
            rides_rows += f"""
            <tr>
                <td>{ride.get('id', '-')}</td>
                <td>{ride.get('date', '-')}</td>
                <td>{ride.get('route', '-')}</td>
                <td>{ride.get('fare', 0):.2f} ₽</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Отчёт водителя</title>
        </head>
        <body>
            <div class="header">
                <div class="logo">🚗 U-BRO TAXI</div>
                <p>Отчёт о поездках</p>
            </div>
            
            <h1>Отчёт водителя: {driver_name}</h1>
            
            <div class="receipt-info">
                <p><strong>Период:</strong> {period_start.strftime('%d.%m.%Y')} - {period_end.strftime('%d.%m.%Y')}</p>
                <p><strong>Всего поездок:</strong> {len(rides)}</p>
            </div>
            
            <h2>Список поездок</h2>
            <table>
                <tr>
                    <th>#</th>
                    <th>Дата</th>
                    <th>Маршрут</th>
                    <th>Сумма</th>
                </tr>
                {rides_rows if rides_rows else '<tr><td colspan="4">Нет поездок за период</td></tr>'}
            </table>
            
            <div class="receipt-info">
                <p><strong>Общая сумма:</strong> {total_earnings:.2f} ₽</p>
                <p><strong>Комиссия сервиса:</strong> {total_commission:.2f} ₽</p>
                <p class="amount"><strong>К выплате:</strong> {total_earnings - total_commission:.2f} ₽</p>
            </div>
            
            <div class="footer">
                <p>Документ сформирован: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        return await self._generate_pdf_from_html(html)
    
    async def generate_balance_statement(
        self,
        user_name: str,
        current_balance: float,
        transactions: list
    ) -> bytes:
        """Генерация выписки по балансу"""
        
        transactions_rows = ""
        for tx in transactions:
            tx_type = "Пополнение" if not tx.get('is_withdraw') else "Списание"
            tx_class = "color: green;" if not tx.get('is_withdraw') else "color: red;"
            transactions_rows += f"""
            <tr>
                <td>{tx.get('id', '-')}</td>
                <td>{tx.get('date', '-')}</td>
                <td>{tx_type}</td>
                <td style="{tx_class}">{tx.get('amount', 0):.2f} ₽</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Выписка по балансу</title>
        </head>
        <body>
            <div class="header">
                <div class="logo">🚗 U-BRO TAXI</div>
                <p>Выписка по счёту</p>
            </div>
            
            <h1>Выписка: {user_name}</h1>
            
            <div class="receipt-info">
                <p><strong>Текущий баланс:</strong></p>
                <p class="amount">{current_balance:.2f} ₽</p>
            </div>
            
            <h2>История операций</h2>
            <table>
                <tr>
                    <th>#</th>
                    <th>Дата</th>
                    <th>Тип</th>
                    <th>Сумма</th>
                </tr>
                {transactions_rows if transactions_rows else '<tr><td colspan="4">Нет операций</td></tr>'}
            </table>
            
            <div class="footer">
                <p>Документ сформирован: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        return await self._generate_pdf_from_html(html)
    
    async def _generate_pdf_from_html(self, html: str) -> bytes:
        """Внутренний метод генерации PDF из HTML"""
        
        if self.weasyprint_available:
            return self._generate_with_weasyprint(html)
        elif self.reportlab_available:
            return self._generate_fallback(html)
        else:
            raise RuntimeError("No PDF generation library available. Install weasyprint or reportlab.")
    
    def _generate_with_weasyprint(self, html: str) -> bytes:
        """Генерация PDF через WeasyPrint"""
        # WeasyPrint 60+ имеет новый API
        html_doc = HTML(string=html)
        pdf = html_doc.write_pdf()
        return pdf
    
    def _generate_fallback(self, html: str) -> bytes:
        """Fallback генерация через ReportLab (без HTML)"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Простой текст (ReportLab не парсит HTML)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "U-BRO TAXI")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, "PDF документ")
        c.drawString(50, height - 110, f"Сгенерирован: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}")
        c.drawString(50, height - 150, "Для полноценной генерации установите WeasyPrint")
        
        c.save()
        buffer.seek(0)
        return buffer.read()


# Глобальный экземпляр генератора
pdf_generator = PDFGenerator()
