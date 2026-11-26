from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Ticket, TicketStatus
from app.schemas import TicketCreate


class InvalidTransition(Exception):
    """Недопустимый переход статуса → 409."""


ALLOWED = {
    TicketStatus.queued: {TicketStatus.processing},
    TicketStatus.processing: {TicketStatus.done, TicketStatus.failed},
    TicketStatus.done: set(),
    TicketStatus.failed: set(),
}


def transition(ticket: Ticket, new_status: TicketStatus) -> None:
    if new_status not in ALLOWED[ticket.status]:
        raise InvalidTransition(
            f"{ticket.status.value} -> {new_status.value} not allowed"
        )
    ticket.status = new_status


async def create_ticket(session: AsyncSession, data: TicketCreate) -> Ticket:
    # идемпотентность: повторный ключ → вернуть существующий, не дубль
    if data.idempotency_key:
        existing = await session.scalar(
            select(Ticket).where(Ticket.idempotency_key == data.idempotency_key)
        )
        if existing:
            return existing

    ticket = Ticket(
        title=data.title,
        description=data.description,
        idempotency_key=data.idempotency_key,
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket