import psycopg2


# удаление и перезапись таблиц
def reset_and_reload_data(conn):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM phones;')
        cur.execute('DELETE FROM users;')
        cur.execute('DROP TABLE IF EXISTS users CASCADE;')
        cur.execute('DROP INDEX IF EXISTS idx_email;')


# создание таблицы
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                email VARCHAR(100) UNIQUE
            );
        ''')
        cur.execute('''
            CREATE INDEX idx_email ON users(email);
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                phone_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                phone_number VARCHAR(50)
            );
        ''')


# добавление нового клиента
def add_customer(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        try:
            cur.execute('''
                INSERT INTO users (first_name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id;
            ''', (first_name, last_name, email))

            user_id = cur.fetchone()[0]

            if phones:
                for phone in phones:
                    add_phone_number(conn, user_id, phone)

        except Exception as e:
            print(f"Ошибка при добавлении клиента: {e}")


# добавление номера телефона
def add_phone_number(conn, user_id, phone):
    with conn.cursor() as cur:
        try:
            cur.execute('''
                INSERT INTO phones (user_id, phone_number)
                VALUES (%s, %s);
            ''', (user_id, phone))

        except Exception as e:
            print(f"Ошибка при добавлении номера телефона: {e}")


# изменение данных о клиенте
def update_customer_info(conn, user_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        try:
            update_fields = []
            update_values = []

            if first_name is not None:
                update_fields.append('first_name = %s')
                update_values.append(first_name)

            if last_name is not None:
                update_fields.append('last_name = %s')
                update_values.append(last_name)

            if email is not None:
                update_fields.append('email = %s')
                update_values.append(email)

            if update_fields:
                update_query = '''
                    UPDATE users
                    SET {}
                    WHERE id=%s;
                '''.format(', '.join(update_fields))

                cur.execute(update_query, update_values + [user_id])

            if phones:
                for phone in phones:
                    add_phone_number(conn, user_id, phone)

            print(f'Данные клиента с ID {user_id} успешно обновлены.')
        except Exception as e:
            print(f"Ошибка при обновлении данных клиента: {e}")


# удаление телефона для существующего клиента
def delete_client_number(conn, user_id, phone):
    with conn.cursor() as cur:
        try:
            cur.execute('''
                DELETE FROM phones
                WHERE user_id = %s AND phone_number = %s;
            ''', (user_id, phone))
        except Exception as e:
            print(f'Ошибка при удалении номера телефона: {e}')


# удаление существующего клиента
def delete_client(conn, user_id):
    with conn.cursor() as cur:
        try:
            cur.execute('''
                DELETE FROM users
                WHERE id = %s;
            ''', (user_id,))
        except Exception as e:
            print(f'Ошибка при удалении клиента: {e}')


# поиск клиента по данным
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        try:
            query = 'SELECT * FROM users WHERE 1=1'
            values = []

            if first_name:
                query += ' AND first_name ILIKE %s'
                values.append(f'%{first_name}%')

            if last_name:
                query += ' AND last_name ILIKE %s'
                values.append(f'%{last_name}%')

            if email:
                query += ' AND email ILIKE %s'
                values.append(f'%{email}%')

            if phone:
                query += ' AND id IN (SELECT user_id FROM phones WHERE phone_number = %s)'
                values.append(phone)

            cur.execute(query, values)
            results = cur.fetchall()
            if results:
                print('Результаты поиска:')
                for row in results:
                    print(f'ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Email: {row[3]}')
            else:
                print(f'Клиент с такими данными не найден.')

        except Exception as e:
            print(f'Ошибка при поиске клиента: {e}')