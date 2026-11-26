import asyncio

from app.db import SessionLocal, Ticket, TicketStatus


async def seed():
    async with SessionLocal() as session:
        # Проверяем, есть ли уже записи
        from sqlalchemy import func, select
        count = await session.scalar(select(func.count()).select_from(Ticket))
        if count > 0:
            print("База уже содержит данные, пропускаем seed.")
            return

        tickets = [
            Ticket(title="Проблема с оплатой", description="Не проходит карта", status=TicketStatus.done),
            Ticket(title="Не приходит SMS", description="Жду код 10 минут", status=TicketStatus.queued),
            Ticket(title="Ошибка 500", description="При нажатии на кнопку", status=TicketStatus.failed, error_reason="Internal Server Error"),
        ]
        session.add_all(tickets)
        await session.commit()
        print("Добавлено 3 тестовых обращения.")

if __name__ == "__main__":
    asyncio.run(seed())