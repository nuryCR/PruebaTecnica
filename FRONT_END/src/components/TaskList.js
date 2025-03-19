import React, { useEffect, useState } from 'react';
import { getTasks, getUsers } from './api';

const TaskList = () => {
    const [tasks, setTasks] = useState([]);
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState('');

    useEffect(() => {
        getUsers().then(response => setUsers(response.data));
        getTasks(selectedUser).then(response => setTasks(response.data));
    }, [selectedUser]);

    return (
        <div>
            <h1>Task List</h1>
            <select onChange={(e) => setSelectedUser(e.target.value)}>
                <option value="">Todos los usuarios</option>
                {users.map(user => (
                    <option key={user.user_id} value={user.user_id}>{user.name}</option>
                ))}
            </select>
            <ul>
                {tasks.map(task => (
                    <li key={task.id}>
                        <h2>{task.title}</h2>
                        <p>{task.description}</p>
                        <p>Status: {task.status}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default TaskList;