import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Ticket, TicketStatus, get_session
from app.schemas import TicketCreate, TicketList, TicketOut
from app.service import InvalidTransition, create_ticket
from app.worker import get_arq_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.arq = await get_arq_pool()
    yield
    await app.state.arq.aclose()


app = FastAPI(title="Ticket Queue", lifespan=lifespan)


@app.exception_handler(InvalidTransition)
async def invalid_transition_handler(request: Request, exc: InvalidTransition):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/tickets", response_model=TicketOut, status_code=201)
async def create(
    data: TicketCreate,
    session: AsyncSession = Depends(get_session),
):
    ticket = await create_ticket(session, data)
    await app.state.arq.enqueue_job("process_ticket", str(ticket.id))
    return ticket


@app.get("/api/tickets", response_model=TicketList)
async def list_tickets(
    status: TicketStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Ticket)
    count_stmt = select(func.count()).select_from(Ticket)
    if status is not None:
        stmt = stmt.where(Ticket.status == status)
        count_stmt = count_stmt.where(Ticket.status == status)

    total = await session.scalar(count_stmt)
    rows = await session.scalars(
        stmt.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    )
    return TicketList(items=list(rows.all()), total=total or 0)


@app.get("/api/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: str, session: AsyncSession = Depends(get_session)):
    try:
        # Преобразуем строку в UUID (для корректной работы с SQLite и Postgres)
        uid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid UUID format")
        
    ticket = await session.get(Ticket, uid)
    if ticket is None:
        raise HTTPException(status_code=404, detail="not found")
    return ticket

# Подключаем метрики Prometheus
Instrumentator().instrument(app).expose(app)