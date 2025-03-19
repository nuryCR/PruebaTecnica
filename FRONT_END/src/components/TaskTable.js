import React, { useEffect, useState } from 'react';
import { getTasks, getUsers, createTask, updateTask } from './api';
import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
    Button, TextField, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem
} from '@mui/material';

const TaskTable = () => {
    const [tasks, setTasks] = useState([]);
    const [users, setUsers] = useState([]);
    const [open, setOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [formValues, setFormValues] = useState({
        title: '',
        description: '',
        status: 'pending',
        user_id: ''
    });

    useEffect(() => {
        getUsers().then(response => setUsers(response.data));
        getTasks().then(response => setTasks(response.data));
    }, []);

    const handleOpen = (task = null) => {
        setEditingTask(task);
        if (task) {
            setFormValues(task);
        } else {
            setFormValues({
                title: '',
                description: '',
                status: 'pending',
                user_id: ''
            });
        }
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormValues({ ...formValues, [name]: value });
    };

    const handleSubmit = () => {
        if (editingTask) {
            updateTask(editingTask.id, formValues).then(() => {
                setTasks(tasks.map(task => (task.id === editingTask.id ? formValues : task)));
            });
        } else {
            createTask(formValues).then(response => {
                setTasks([...tasks, response.data]);
            });
        }
        handleClose();
    };

    return (
        <div>
            <Button variant="contained" color="primary" onClick={() => handleOpen()}>
                Add Task
            </Button>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Title</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>User</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tasks.map((task) => (
                            <TableRow key={task.id}>
                                <TableCell>{task.title}</TableCell>
                                <TableCell>{task.description}</TableCell>
                                <TableCell>{task.status}</TableCell>
                                <TableCell>{task.user_name}</TableCell>
                                <TableCell>
                                    <Button variant="contained" color="secondary" onClick={() => handleOpen(task)}>
                                        Edit
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>{editingTask ? 'Edit Task' : 'Add Task'}</DialogTitle>
                <DialogContent>
                    <TextField
                        margin="dense"
                        label="Title"
                        name="title"
                        value={formValues.title}
                        onChange={handleChange}
                        fullWidth
                    />
                    <TextField
                        margin="dense"
                        label="Description"
                        name="description"
                        value={formValues.description}
                        onChange={handleChange}
                        fullWidth
                    />
                    <TextField
                        margin="dense"
                        label="Status"
                        name="status"
                        value={formValues.status}
                        onChange={handleChange}
                        select
                        fullWidth
                    >
                        <MenuItem value="pending">Pending</MenuItem>
                        <MenuItem value="in progress">In Progress</MenuItem>
                        <MenuItem value="completed">Completed</MenuItem>
                    </TextField>
                    <TextField
                        margin="dense"
                        label="User"
                        name="user_id"
                        value={formValues.user_id}
                        onChange={handleChange}
                        select
                        fullWidth
                    >
                        {users.map(user => (
                            <MenuItem key={user.user_id} value={user.user_id}>
                                {user.name}
                            </MenuItem>
                        ))}
                    </TextField>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleSubmit} color="primary">
                        {editingTask ? 'Update' : 'Add'}
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

export default TaskTable;
