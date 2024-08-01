if False:

    from backend.functionality.serverConnectors import AbsClient


    HOST = '127.0.0.1'
    PORT = 8899

    def connectToServer(func):
        async def wrapper(self, *args, **kwargs):
            # get the task from the function
            # create client
            # run
            # return
            ##result = func(self, *args, **kwargs)
            try:
                task = func(self, *args, **kwargs)
                client = AbsClient(HOST, PORT)
                answer, succeeded = await client.runClient(task)
                if not succeeded:
                    return None
                return answer
            except:
                return None
        return wrapper



    class DatabaseHandler:
        
        def __init__(self):
            """Initializes the class.

            :param None:
            :return: None
            """
            self.usersColumns = [
                'username',
                'password',
                'planId',
                'lastCreation',
                'creationCount'
            ]
            self.plansColumns = [
                'planId',
                'planName',
                'price',
                'filesPerDay'
            ]

        
        @connectToServer
        def selectExists(self, table, column, value):
            task = {'action' : 'selectExists', 'data' : {
                'table' : table,
                'column' : column,
                'value' : value
            }}
            return task
        
        @connectToServer
        def select(self, table, columns, conditionColumn, condition, conditionValue):
            task = {'action' : 'select', 'data' : {
                'table' : table,
                'columns' : columns,
                'conditionColumn' : conditionColumn,
                'condition' : condition,
                'conditionValue' : conditionValue
            }}
            return task
        
        @connectToServer
        def selectAll(self, table):
            task = {'action' : 'selectAll', 'data' : {
                'table' : table
            }}
            return task
        
        @connectToServer
        def insertInto(self, table, columns, values):
            task = {'action' : 'insertInto', 'data' : {
                'table' : table,
                'columns' : columns,
                'values' : values
            }}
            return task

        @connectToServer
        def update(self, table, columnToModify, newValue, columnToSearch, valueToSearch):
            task = {'action' : 'update', 'data' : {
                'table' : table,
                'columnToModify' : columnToModify,
                'newValue' : newValue,
                'columnToSearch' : columnToSearch,
                'valueToSearch' : valueToSearch
            }}
            return task
        
        @connectToServer
        def joinSelect(self, tTable, tColumn, sTable, sColumn, sValue, tCommonColumn, sCommonColumn = None):
            task = {'action' : 'joinSelect', 'data' : {
                'tTable' : tTable,
                'tColumn' : tColumn,
                'sTable' : sTable,
                'sColumn' : sColumn,
                'sValue' : sValue,
                'tCommonColumn' : tCommonColumn,
                'sCommonColumn'  :  sCommonColumn
            }}
            return task



import os
import threading
import configparser
import mysql.connector


connectionLock = threading.Lock()

def connectToDatabase(func):
    """
    Connects to the database and executes the given function.

    :param func: The function to be executed with the database connection.
    :return: The result of the function execution.
    """
    def wrapper(self, *args, **kwargs):
        try:
            with connectionLock:
                cnx, cursor = openConnection()
                result = func(self, cnx, cursor, *args, **kwargs)
                closeConnection(cnx, cursor)
            return result
        except Exception as e:
            print(e)
            return False
    return wrapper

def openConnection():
    """
    Opens a connection to the MySQL database.

    :return: A tuple containing the connection object and the cursor object.
    """
    config = configparser.ConfigParser()
    dirPath = os.path.dirname(os.path.realpath(__file__))
    configFilePath = os.path.join(dirPath, "../../config.ini")
    configFilePath = os.path.abspath(configFilePath)
    config.read(configFilePath)
    user, password = config['DATABASE']['user'], config['DATABASE']['password']
    cnx = mysql.connector.connect(
        user=user,
        password=password,
        host='localhost',
        database='stega'
    )
    cursor = cnx.cursor()
    return cnx, cursor

def closeConnection(cnx, cursor):
    """
    Close the connection to the database.

    :param cnx: The database connection object.
    :type cnx: Any object implementing the database connection interface.

    :param cursor: The database cursor object.
    :type cursor: Any object implementing the database cursor interface.

    :return: None
    :rtype: NoneType
    """
    cursor.close()
    cnx.close()


class DatabaseHandler:
    
    def __init__(self):
        self.usersColumns = [
            'username',
            'password',
            'planId',
            'lastCreation',
            'creationCount'
        ]
        self.plansColumns = [
            'planId',
            'planName',
            'price',
            'filesPerDay'
        ]
        self.initialSetup()
        

    def initialSetup(self):
        """
        Sets up the initial database tables and inserts default values if necessary.

        :return: None
        """
        result = self.createTables()
        usersExist, plansExist = result
        if not plansExist:
            plans = [
                [0, 'bronze', 0, 1],
                [1, 'silver', 5, 3],
                [2, 'gold', 15, 10],
                [3, 'platinum', 30, -1]
            ]
            for plan in plans:
                self.insertInto('plans', self.plansColumns, plan)
    
    @connectToDatabase
    def createTables(self, cnx, cursor):
        """
        Create tables in the database if they do not already exist.

        :param cnx: The database connection.
        :param cursor: The database cursor.
        :return: A tuple indicating whether the 'users' table and 'plans' table exist in the database.
        :rtype: tuple(bool, bool)

        """
        def tableExists(cursor, table):
            """
            :param cursor: the cursor object for executing the SQL query
            :param table: the name of the table to check if exists
            :return: True if table exists, False otherwise
            """
            query = ("SELECT COUNT(*) "
                "FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s")
            cursor.execute(query, ('stega', table))
            if cursor.fetchone()[0] == 1:
                return True
            return False
        usersExist, plansExist = tableExists(cursor, 'users'), tableExists(cursor, 'plans')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                planId INT NOT NULL,
                planName VARCHAR(32) NOT NULL,
                price FLOAT NOT NULL,
                filesPerDay INT NOT NULL,
                PRIMARY KEY (planNum)
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(32) NOT NULL,
                password VARCHAR(32) NOT NULL,
                planId INT NOT NULL,
                lastCreation DATE NOT NULL,
                creationCount INT NOT NULL,
                verified TINYINT(1) NOT NULL,
                email VARCHAR(150) NOT NULL,
                PRIMARY KEY (username),
                FOREIGN KEY	(planId) REFERENCES plans(planId)
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changePass (
                username VARCHAR(32) NOT NULL,
                verCode VARCHAR(6) NOT NULL,
                PRIMARY KEY (username),
                FOREIGN KEY	(username) REFERENCES users(username)
            );
        ''')
        cnx.commit()
        
        return usersExist, plansExist
    
    
    @connectToDatabase
    def selectExists(self, cnx, cursor, table, column, value):
        """
        :param cnx: The connection object to the database.
        :param cursor: The cursor object to execute the SQL query.
        :param table: The name of the table to check for existence.
        :param column: The column name to filter the query.
        :param value: The value to check in the specified column.
        :return: A boolean value indicating whether the specified value exists in the specified column of the table.

        """
        query = f'SELECT EXISTS(SELECT * FROM {table} WHERE {column} = %s) as exist'
        cursor.execute(query, (value,))
        result = cursor.fetchone()[0]
        return result
    
    @connectToDatabase
    def select(self, cnx, cursor, table, columns, conditionColumn, condition, conditionValue):
        """
        Perform a SELECT query on a database table with a specified condition.

        :param cnx: MySQL connection object.
        :param cursor: MySQL cursor object.
        :param table: Name of the table to perform the SELECT query on.
        :param columns: List of columns to retrieve in the SELECT query.
        :param conditionColumn: Name of the column to apply the condition on.
        :param condition: Condition operator (e.g., '=', '>', '<').
        :param conditionValue: Value to be compared in the condition.
        :return: The value of the first column of the result set if found, otherwise None.
        """
        columns = ', '.join(columns)
        query = f'SELECT {columns} FROM {table} WHERE {conditionColumn} {condition} %s'
        cursor.execute(query, (conditionValue,))
        result = cursor.fetchone()
        if not result:
            return None
        return result[0]
    
    @connectToDatabase
    def selectAll(self, cnx, cursor, table):
        """
        Selects all rows from the specified table.

        :param cnx: The database connection object.
        :param cursor: The database cursor object.
        :param table: The name of the table to select from.
        :return: A list of all rows from the specified table.
        """
        query = f'SELECT * FROM {table}'
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    
    @connectToDatabase
    def insertInto(self, cnx, cursor, table, columns, values):
        """
        Insert values into a specified table in the database.

        :param cnx: The database connection.
        :type cnx: connection

        :param cursor: The database cursor.
        :type cursor: cursor

        :param table: The name of the table to insert into.
        :type table: str

        :param columns: The columns to insert values into.
        :type columns: list

        :param values: The values to insert.
        :type values: list

        :return: True if the insert operation is successful.
        :rtype: bool
        """
        columns = ', '.join(columns)
        values = tuple(values)
        placeholders = ', '.join(['%s'] * len(values))
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        cursor.execute(query, values)
        cnx.commit()
        return True

    @connectToDatabase
    def update(self, cnx, cursor, table, columnToModify, newValue, columnToSearch, valueToSearch):
        """
        Update the value of a column in a table based on a condition.

        :param cnx: The connection object to the database.
        :param cursor: The cursor object to execute SQL queries.
        :param table: The name of the table where the update will be performed.
        :param columnToModify: The name of the column to be modified.
        :param newValue: The new value to set in the specified column.
        :param columnToSearch: The name of the column used as a condition.
        :param valueToSearch: The value to search for in the columnToSearch.
        :return: True if the update was successful, False otherwise.
        """
        query = f'UPDATE {table} SET {columnToModify} = %s WHERE {columnToSearch} = %s'
        cursor.execute(query, (newValue, valueToSearch))
        cnx.commit()
        return True

    @connectToDatabase
    def joinSelect(self, cnx, cursor, tTable, tColumn, sTable, sColumn, sValue, tCommonColumn, sCommonColumn=None):
        """
        Perform a join select query on two tables.

        :param cnx: The connection object to the database.
        :param cursor: The cursor object to execute SQL queries.
        :param tTable: The target table to select from.
        :param tColumn: The target column to select.
        :param sTable: The source table to join.
        :param sColumn: The source column to join.
        :param sValue: The value to filter on the source table's column.
        :param tCommonColumn: The common column between target and source table.
        :param sCommonColumn: The common column between source and target table (defaults to tCommonColumn).
        :return: The value of the selected target column, or None if no result is found.
        """
        sCommonColumn = sCommonColumn if sCommonColumn else tCommonColumn
        query = f'''
            SELECT t.{tColumn}
            FROM {tTable} t
            INNER JOIN {sTable} b ON t.{tCommonColumn} = b.{sCommonColumn}
            WHERE b.{sColumn} = %s
        '''
        cursor.execute(query, (sValue,))
        result = cursor.fetchone()
        if not result:
            return None
        return result[0]

    @connectToDatabase
    def delete(self, cnx, cursor, table, columnToDeleteBy, valueToDeleteBy):
        query = f'DELETE FROM {table} WHERE {columnToDeleteBy} = %s'
        print(query)
        cursor.execute(query, (valueToDeleteBy,))
        cnx.commit()
        return True



