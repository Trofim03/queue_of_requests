import pytest

from app.db import Ticket, TicketStatus
from app.service import InvalidTransition, transition


def test_invalid_transition():
    ticket = Ticket(title="T", description="D", status=TicketStatus.done)
    # Нельзя перевести из done в processing
    with pytest.raises(InvalidTransition):
        transition(ticket, TicketStatus.processing)

def test_valid_transition():
    ticket = Ticket(title="T", description="D", status=TicketStatus.queued)
    transition(ticket, TicketStatus.processing)
    assert ticket.status == TicketStatus.processing