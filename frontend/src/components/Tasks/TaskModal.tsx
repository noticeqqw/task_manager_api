import { useState } from 'react';
import { tasksApi } from '../../api';
import type { Task } from '../../types';
import './TaskModal.css';

interface TaskModalProps {
  task: Task | null;
  onClose: () => void;
  onSave: (task: Task) => void;
}

export default function TaskModal({ task, onClose, onSave }: TaskModalProps) {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [status, setStatus] = useState(task?.status || 'todo');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const isEditing = !!task;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!title.trim()) {
      setError('Название обязательно');
      return;
    }

    setIsLoading(true);

    try {
      let savedTask: Task;
      
      if (isEditing) {
        savedTask = await tasksApi.update(task.id, {
          title,
          description: description || undefined,
          status,
        });
      } else {
        // Генерируем idempotency key для новых задач
        const idempotencyKey = crypto.randomUUID();
        savedTask = await tasksApi.create(
          {
            title,
            description: description || undefined,
            status,
          },
          idempotencyKey
        );
      }
      
      onSave(savedTask);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        <div className="modal-header">
          <h2>{isEditing ? 'Редактировать задачу' : 'Новая задача'}</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="title">Название</label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Введите название задачи"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Описание</label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Опишите задачу подробнее..."
              />
            </div>

            <div className="form-group">
              <label>Статус</label>
              <div className="status-options">
                <div
                  className={`status-option ${status === 'todo' ? 'selected todo' : ''}`}
                  onClick={() => setStatus('todo')}
                >
                  <div className="status-icon">📋</div>
                  <div className="status-label">К выполнению</div>
                </div>
                <div
                  className={`status-option ${status === 'in_progress' ? 'selected in_progress' : ''}`}
                  onClick={() => setStatus('in_progress')}
                >
                  <div className="status-icon">🔄</div>
                  <div className="status-label">В работе</div>
                </div>
                <div
                  className={`status-option ${status === 'done' ? 'selected done' : ''}`}
                  onClick={() => setStatus('done')}
                >
                  <div className="status-icon">✅</div>
                  <div className="status-label">Готово</div>
                </div>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? 'Сохранение...' : (isEditing ? 'Сохранить' : 'Создать')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
