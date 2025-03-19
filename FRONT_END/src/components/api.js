import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8002',
});

export const getUsers = () => api.get('/users');
export const getTasks = (user_id) => api.get('/tasks', { params: { user_id } });
export const createTask = (task) => api.post('/tasks', task);
export const updateTask = (task_id, task) => api.put(`/tasks/${task_id}`, task);