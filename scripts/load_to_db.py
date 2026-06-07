import sqlite3
import pandas as pd
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'bank.db'
CLEAN_DATA_PATH = BASE_DIR / 'data' / 'transactions_clean.csv'


def create_schema(conn):
    """Создаёт таблицы clients, accounts, transactions"""
    cursor = conn.cursor()

    # Создаём таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY,
            client_name TEXT,
            registration_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            client_id INTEGER,
            account_number TEXT,
            account_type TEXT,
            open_date TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id INTEGER,
            transaction_date TEXT,
            amount REAL,
            transaction_type TEXT,
            is_inflow INTEGER,
            inflow_amount REAL,
            outflow_amount REAL,
            description TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    ''')

    conn.commit()


def load_clients_and_accounts(conn, df):
    """Загружает клиентов и счета из данных"""

    # Конвертируем дату в datetime, если она строка
    if isinstance(df['transaction_date'].iloc[0], str):
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Получаем уникальных клиентов (пока один)
    clients_df = df[['client_id']].drop_duplicates()
    clients_df['client_name'] = 'Клиент 1'
    # Используем .iloc[0] для получения первого значения
    min_date = df['transaction_date'].min()
    clients_df['registration_date'] = min_date.strftime('%Y-%m-%d')

    clients_df.to_sql('clients', conn, if_exists='replace', index=False)

    # Загружаем счета
    accounts_df = df[['account_id', 'client_id', 'account_no']].drop_duplicates()
    accounts_df = accounts_df.rename(columns={'account_no': 'account_number'})
    accounts_df['account_type'] = 'Текущий'
    # Используем ту же дату
    accounts_df['open_date'] = min_date.strftime('%Y-%m-%d')

    accounts_df.to_sql('accounts', conn, if_exists='replace', index=False)

    return len(clients_df), len(accounts_df)


def load_transactions(conn, df):
    """Загружает транзакции"""

    # Подготавливаем транзакции
    transactions_df = df[[
        'transaction_id', 'account_id', 'transaction_date',
        'amount', 'is_inflow', 'inflow_amount', 'outflow_amount', 'description'
    ]].copy()

    # Конвертируем даты в строки (если ещё не строки)
    if not isinstance(transactions_df['transaction_date'].iloc[0], str):
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date']).dt.strftime(
            '%Y-%m-%d')

    # Определяем тип транзакции
    transactions_df['transaction_type'] = transactions_df['is_inflow'].apply(
        lambda x: 'DEPOSIT' if x == 1 else 'WITHDRAWAL'
    )

    transactions_df.to_sql('transactions', conn, if_exists='replace', index=False)

    return len(transactions_df)


def main():
    # Удаляем старую базу
    if DB_PATH.exists():
        DB_PATH.unlink()
    df = pd.read_csv(CLEAN_DATA_PATH)


    # Создаём подключение к БД
    conn = sqlite3.connect(DB_PATH)

    try:
        # Создаём схему
        create_schema(conn)

        # Загружаем клиентов и счета
        num_clients, num_accounts = load_clients_and_accounts(conn, df)

        # Загружаем транзакции
        num_transactions = load_transactions(conn, df)

        # Проверяем результат
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]

        print(f"\nБД успешно создана!")


    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()