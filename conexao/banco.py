import mysql.connector
from mysql.connector import Error

def conexao():
    try:
        connection = mysql.connector.connect(
            host=" database-1.cth3fbnggspb.sa-east-1.rds.amazonaws.com",
            user="jetset",
            password="jAqrps2FtAKh4gDY1mM7",
            database="agentesocial"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None