import asyncio
import logging
import random

from arq import create_pool
from arq.connections import RedisSettings

from app.config import settings
from app.db import SessionLocal, Ticket, TicketStatus
from app.service import InvalidTransition, transition

logger = logging.getLogger(__name__)


async def process_ticket(ctx, ticket_id: str) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            ticket = await session.get(Ticket, ticket_id, with_for_update=True)

            if ticket is None:
                logger.warning("ticket %s not found", ticket_id)
                return

            # идемпотентность: повторный запуск не переобрабатывает
            if ticket.status != TicketStatus.queued:
                logger.info("ticket %s already %s, skip", ticket_id, ticket.status)
                return

            transition(ticket, TicketStatus.processing)

        # имитация работы 2–5 сек
        await asyncio.sleep(
            random.uniform(settings.processing_delay_min, settings.processing_delay_max)
        )

        async with session.begin():
            ticket = await session.get(Ticket, ticket_id, with_for_update=True)
            try:
                if settings.worker_force_error:  # сюда можно подставить флаг ошибки
                    raise RuntimeError("boom")
                transition(ticket, TicketStatus.done)
            except (InvalidTransition, RuntimeError) as exc:
                logger.exception("ticket %s failed: %s", ticket_id, exc)
                ticket.status = TicketStatus.failed
                ticket.error_reason = str(exc)


class WorkerSettings:
    functions = [process_ticket]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_tries = 3          # ретраи
    job_timeout = 30


async def get_arq_pool():
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))