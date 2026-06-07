-- Таблица клиентов
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY,
    client_name TEXT,
    client_region TEXT
);

-- Таблица счетов
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY,
    client_id INTEGER,
    account_type TEXT,
    open_date TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

-- Таблица транзакций
CREATE TABLE IF NOT EXISTS transactions (
    trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    trans_date TEXT,
    amount REAL,
    trans_type TEXT,
    category TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(trans_date);