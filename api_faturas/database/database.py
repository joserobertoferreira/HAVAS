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

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f'Exception: {exc_type}')
            print(f'Exception: {exc_value}')

        self.disconnect()
