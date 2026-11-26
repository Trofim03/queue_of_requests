export type TicketStatus = 'queued' | 'processing' | 'done' | 'failed';

export interface Ticket {
  id: string;
  title: string;
  description: string;
  status: TicketStatus;
  error_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
}

const API_URL = '/api';

export async function fetchTickets(): Promise<TicketListResponse> {
  const res = await fetch(`${API_URL}/tickets`);
  if (!res.ok) throw new Error('Failed to fetch tickets');
  return res.json();
}

export async function fetchTicket(id: string): Promise<Ticket> {
  const res = await fetch(`${API_URL}/tickets/${id}`);
  if (!res.ok) throw new Error('Failed to fetch ticket');
  return res.json();
}

export async function createTicket(data: { title: string; description: string }): Promise<Ticket> {
  const res = await fetch(`${API_URL}/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create ticket');
  return res.json();
}