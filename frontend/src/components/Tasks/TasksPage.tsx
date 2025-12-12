import { useState, useEffect } from 'react';
import { tasksApi } from '../../api';
import type { Task } from '../../types';
import TaskCard from './TaskCard';
import TaskModal from './TaskModal';
import './Tasks.css';

type FilterStatus = 'all' | 'todo' | 'in_progress' | 'done';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<FilterStatus>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const data = await tasksApi.getAll();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const getFilterCount = (status: FilterStatus) => {
    if (status === 'all') return tasks.length;
    return tasks.filter((t) => t.status === status).length;
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setIsModalOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('Вы уверены, что хотите удалить эту задачу?')) {
      try {
        await tasksApi.delete(taskId);
        setTasks(tasks.filter((t) => t.id !== taskId));
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const handleSaveTask = async (task: Task) => {
    if (editingTask) {
      setTasks(tasks.map((t) => (t.id === task.id ? task : t)));
    } else {
      setTasks([task, ...tasks]);
    }
    setIsModalOpen(false);
    setEditingTask(null);
  };

  const handleStatusChange = async (task: Task, newStatus: string) => {
    try {
      const updated = await tasksApi.update(task.id, { status: newStatus });
      setTasks(tasks.map((t) => (t.id === task.id ? updated : t)));
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="tasks-page">
      <div className="page-header">
        <h2>Мои задачи</h2>
        <button className="btn-create" onClick={handleCreateTask}>
          <span>➕</span>
          Новая задача
        </button>
      </div>

      <div className="filters">
        {(['all', 'todo', 'in_progress', 'done'] as FilterStatus[]).map((status) => (
          <button
            key={status}
            className={`filter-btn ${filter === status ? 'active' : ''}`}
            onClick={() => setFilter(status)}
          >
            {status === 'all' && 'Все'}
            {status === 'todo' && 'К выполнению'}
            {status === 'in_progress' && 'В работе'}
            {status === 'done' && 'Готово'}
            <span className="filter-count">{getFilterCount(status)}</span>
          </button>
        ))}
      </div>

      {filteredTasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <h3>Нет задач</h3>
          <p>
            {filter === 'all'
              ? 'Создайте первую задачу, чтобы начать работу'
              : 'Нет задач с таким статусом'}
          </p>
          {filter === 'all' && (
            <button className="btn-create" onClick={handleCreateTask}>
              <span>➕</span>
              Создать задачу
            </button>
          )}
        </div>
      ) : (
        <div className="tasks-grid">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onEdit={() => handleEditTask(task)}
              onDelete={() => handleDeleteTask(task.id)}
              onStatusChange={(status) => handleStatusChange(task, status)}
            />
          ))}
        </div>
      )}

      {isModalOpen && (
        <TaskModal
          task={editingTask}
          onClose={() => {
            setIsModalOpen(false);
            setEditingTask(null);
          }}
          onSave={handleSaveTask}
        />
      )}
    </div>
  );
}
