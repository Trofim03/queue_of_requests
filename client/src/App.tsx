import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTickets, createTicket, type Ticket } from './api';

function App() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  // 1. Получение списка с polling каждые 2 секунды
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: fetchTickets,
    refetchInterval: 2000, // Автообновление
  });

  // 2. Создание тикета
  const mutation = useMutation({
    mutationFn: createTicket,
    onSuccess: () => {
      setTitle('');
      setDescription('');
      queryClient.invalidateQueries({ queryKey: ['tickets'] }); // Мгновенно обновить список
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    mutation.mutate({ title, description });
  };

  // Состояния загрузки и ошибки
  if (isLoading) return <div className="p-4">Загрузка...</div>;
  if (isError) return <div className="p-4 text-red-500">Ошибка: {error.message}</div>;

  return (
    <div className="max-w-2xl mx-auto p-4 font-sans">
      <h1 className="text-2xl font-bold mb-4">Очередь обращений</h1>

      {/* Форма создания */}
      <form onSubmit={handleSubmit} className="mb-6 p-4 border rounded bg-gray-50">
        <div className="mb-2">
          <input
            type="text"
            placeholder="Заголовок"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div className="mb-2">
          <textarea
            placeholder="Описание"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 border rounded"
            rows={3}
          />
        </div>
        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {mutation.isPending ? 'Создание...' : 'Создать обращение'}
        </button>
        {mutation.isError && <p className="text-red-500 mt-2">Ошибка при создании</p>}
      </form>

      {/* Список тикетов */}
      {data?.items.length === 0 ? (
        <div className="text-gray-500 text-center p-8 border rounded border-dashed">
          Пока нет ни одного обращения. Создайте первое!
        </div>
      ) : (
        <ul className="space-y-3">
          {data?.items.map((ticket: Ticket) => (
            <li key={ticket.id} className="p-4 border rounded shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="font-semibold">{ticket.title}</h2>
                  <p className="text-sm text-gray-600">{ticket.description}</p>
                </div>
                <StatusBadge status={ticket.status} />
              </div>
              {ticket.error_reason && (
                <p className="text-sm text-red-500 mt-2">Ошибка: {ticket.error_reason}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Компонент бейджа статуса
function StatusBadge({ status }: { status: Ticket['status'] }) {
  const colors = {
    queued: 'bg-gray-200 text-gray-800',
    processing: 'bg-yellow-200 text-yellow-800',
    done: 'bg-green-200 text-green-800',
    failed: 'bg-red-200 text-red-800',
  };
  return (
    <span className={`px-2 py-1 text-xs font-bold rounded uppercase ${colors[status]}`}>
      {status}
    </span>
  );
}

export default App;