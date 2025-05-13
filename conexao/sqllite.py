import sqlite3

def conexaosqllt():
    """Retorna a conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect("agentesocial.db")  # Cria ou conecta ao banco SQLite
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def inicializar_banco():
    """Inicializa o banco de dados e cria a tabela de configurações, se não existir."""
    conn = conexaosqllt()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_no_whatsapp TEXT NOT NULL,
                    sincronizado    TEXT NULL
                ) 
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar a tabela: {e}")
        finally:
            conn.close()