import React, { useState } from 'react';
import { createTask, updateTask } from './api';

const TaskForm = ({ task, onSubmit }) => {
    const [title, setTitle] = useState(task ? task.title : '');
    const [description, setDescription] = useState(task ? task.description : '');
    const [status, setStatus] = useState(task ? task.status : 'pending');
    const [user_id, setUserId] = useState(task ? task.user_id : '');

    const handleSubmit = (e) => {
        e.preventDefault();
        const newTask = { title, description, status, user_id };
        if (task) {
            updateTask(task.id, newTask).then(() => onSubmit());
        } else {
            createTask(newTask).then(() => onSubmit());
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
            />
            <textarea
                placeholder="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            />
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="pending">Pending</option>
                <option value="in progress">In Progress</option>
                <option value="completed">Completed</option>
            </select>
            <input
                type="number"
                placeholder="User ID"
                value={user_id}
                onChange={(e) => setUserId(e.target.value)}
            />
            <button type="submit">{task ? 'Update Task' : 'Create Task'}</button>
        </form>
    );
};

export default TaskForm;