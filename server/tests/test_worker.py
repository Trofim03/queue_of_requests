import pytest
from app.worker import process_ticket
from app.db import SessionLocal, Ticket, TicketStatus
from app.config import settings

@pytest.mark.asyncio
async def test_worker_error():
    # Включаем принудительную ошибку
    settings.worker_force_error = True
    
    async with SessionLocal() as session:
        ticket = Ticket(title="Err", description="D")
        session.add(ticket)
        await session.commit()
        ticket_id = str(ticket.id)
    
    # Запускаем воркер напрямую
    await process_ticket({}, ticket_id)
    
    # Проверяем результат в БД
    async with SessionLocal() as session:
        ticket = await session.get(Ticket, ticket_id)
        assert ticket.status == TicketStatus.failed
        assert ticket.error_reason == "boom"
    
    settings.worker_force_error = False # Сбрасываем