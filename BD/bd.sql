-- Crear la tabla 'users'
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crear la tabla 'tasks'
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) CHECK (status IN ('pending', 'in progress', 'completed')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE
);
