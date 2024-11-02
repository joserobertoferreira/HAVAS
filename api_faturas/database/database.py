from typing import Any, Dict

import pyodbc


class DatabaseConnection:
    def __init__(self, server, database, username, password):
        self.validate_params(server, database, username, password)
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None

    @staticmethod
    def build_connection_string(server, database, username, password):
        return (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )

    @staticmethod
    def validate_params(server, database, username, password):
        if not server or not database or not username or not password:
            raise ValueError('All connection parameters must be provided.')

    def connect(self):
        try:
            connection_string = self.build_connection_string(
                self.server, self.database, self.username, self.password
            )
            self.connection = pyodbc.connect(connection_string)
            return {'status': 'success', 'message': 'Connection successful'}
        except pyodbc.Error as e:
            return {'status': 'error', 'message': f'Error connecting to database: {e}'}

    def disconnect(self):
        if self.connection:
            self.connection.close()
            return {'status': 'success', 'message': 'Connection closed'}

        return {'status': 'info', 'message': 'No active connection to close'}

    def execute_query(self, query):
        if not self.connection:
            return {'status': 'error', 'message': 'No active connection', 'data': None}

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            columns_names = [column[0] for column in cursor.description]

            results = [
                {
                    columns_names[index]: row[index]
                    for index in range(len(columns_names))
                }
                for row in cursor.fetchall()
            ]

            return {
                'status': 'success',
                'message': 'Query executed successfully',
                'columns': columns_names,
                'data': results,
            }
        except pyodbc.Error as e:
            return {
                'status': 'error',
                'message': f'Error executing query: {e}',
                'data': None,
            }

    def execute_update(
        self,
        table_name: str,
        set_columns: list,
        set_values: list,
        where_clauses: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Atualiza registros em uma tabela específica do banco de dados com múltiplas
        condições no WHERE.

        Parâmetros:
        - table_name: nome da tabela a ser atualizada
        - set_columns: lista com o nome das colunas a serem atualizadas
        - set_values: lista com os valores correspondentes às colunas a serem
          atualizadas
        - where_conditions: dicionário onde as chaves são as colunas e os valores são as
          condições do WHERE

        Exemplo de uso:
        update_table("Clientes", ["Nome", "Idade"], ["João", 30], {"ID": 1,
          "Status": "ativo"})
        """

        if not self.connection:
            return {'status': 'error', 'message': 'No active connection', 'data': None}

        # Build the SET clause dynamically with placeholders
        set_clause = ', '.join([f'{column} = ?' for column in set_columns])

        # Build the WHERE clause dynamically with multiple conditions
        where_clause = ' AND '.join([
            f'{column} = ?' for column in where_clauses.keys()
        ])

        # Build the query with the SET and WHERE clauses
        query = f'UPDATE {table_name} SET {set_clause} WHERE {where_clause}'

        # Prepare the values to be updated
        values = set_values + list(where_clauses.values())

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()

            return {
                'status': 'success',
                'message': 'Update executed successfully',
            }
        except pyodbc.Error as e:
            return {
                'status': 'error',
                'message': f'Error executing query: {e}',
                'data': None,
            }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f'Exception: {exc_type}')
            print(f'Exception: {exc_value}')

        self.disconnect()
