import type { Task } from '../../types';

interface TaskCardProps {
  task: Task;
  onEdit: () => void;
  onDelete: () => void;
  onStatusChange: (status: string) => void;
}

export default function TaskCard({ task, onEdit, onDelete, onStatusChange }: TaskCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      todo: 'К выполнению',
      in_progress: 'В работе',
      done: 'Готово',
    };
    return labels[status] || status;
  };

  const handleStatusClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const statuses = ['todo', 'in_progress', 'done'];
    const currentIndex = statuses.indexOf(task.status);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];
    onStatusChange(nextStatus);
  };

  return (
    <div className={`task-card status-${task.status}`} onClick={onEdit}>
      <div className="task-card-header">
        <h3>{task.title}</h3>
        <span 
          className={`task-status ${task.status}`}
          onClick={handleStatusClick}
          title="Клик для смены статуса"
        >
          {getStatusLabel(task.status)}
        </span>
      </div>
      
      {task.description && (
        <p className="task-card-description">{task.description}</p>
      )}
      
      <div className="task-card-footer">
        <span className="task-date">
          📅 {formatDate(task.created_at)}
        </span>
        
        <div className="task-actions">
          <button
            className="task-action-btn"
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
            title="Редактировать"
          >
            ✏️
          </button>
          <button
            className="task-action-btn delete"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            title="Удалить"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
}
