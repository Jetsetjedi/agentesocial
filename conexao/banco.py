import mysql.connector
from mysql.connector import Error

def conexao():
    try:
        connection = mysql.connector.connect(
            host="vbdatabase.mysql.dbaas.com.br",
            user="vbdatabase",
            password="Sagrado@42",
            database="vbdatabase"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None