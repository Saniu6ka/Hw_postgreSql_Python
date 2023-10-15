import psycopg2
from functions import reset_and_reload_data, create_db, add_customer, add_phone_number, update_customer_info, delete_client_number, find_client,delete_client

# вызов функций
if __name__ == "__main__":
    with psycopg2.connect(database='Hw_postgreSql_Python', user='postgres', password='mivida1') as conn:
        reset_and_reload_data(conn)
        create_db(conn)
        add_customer(conn, 'Антон', 'Петров', 'petrova@gmail.com', [+995555733902])
        add_customer(conn, 'Андрей', 'Васечкин', 'vasutka@mail.ru', [+995557566382])
        add_phone_number(conn, 1, '+995587321987')
        update_customer_info(conn, 1, last_name='Сироткин')
        delete_client_number(conn, 2, '+995557566382')
        find_client(conn, email='vasutka@mail.ru')
        delete_client(conn, 2)
        find_client(conn, phone='+995587321987')
    conn.close()