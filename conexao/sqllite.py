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
            # Criação da tabela local de configuração
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configuracoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome_no_whatsapp TEXT NOT NULL,
                        sincronizado    TEXT NULL
                    ) 
            """)
            # Criação da tabela usuarios local
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL,
                        senha TEXT NOT NULL
                    )
            """)
            # Criação da tabela de categorias
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categorias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL UNIQUE
                    )
            """)
            # Criação da tabela de produtos
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome         TEXT NOT NULL,
                        observacao   TEXT NOT NULL,
                        valor_venda REAL NOT NULL DEFAULT 0.0,
                        categoria_id INTEGER NOT NULL,
                           
                        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
                    )    

            """)
            # Tabela para persistir atendimentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atendimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contato TEXT NOT NULL UNIQUE,
                    estado TEXT NOT NULL,
                    categoria TEXT,
                    produto TEXT,
                    endereco TEXT,
                    ultima_interacao DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Tabela para registrar pedidos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contato TEXT NOT NULL,
                    categoria TEXT,
                    produto TEXT,
                    endereco TEXT,
                    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Adiciona colunas novas se não existirem em (produtos)
            try:
                cursor.execute("ALTER TABLE produtos ADD COLUMN observacao TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # Já existe

            # Adicionando 'valor_venda'
            try:
                cursor.execute("ALTER TABLE produtos ADD COLUMN valor_venda REAL NOT NULL DEFAULT 0.0")
            except sqlite3.OperationalError:
                pass  # Já existe
            
            
            # Adicionando campos na tabela pedidos    
            try:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN observacao TEXT")
            except sqlite3.OperationalError:
                pass  # Já existe

            try:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN valor REAL")
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN nome_cliente TEXT")
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN referencia TEXT")
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN quantidade INTEGER;")
            except sqlite3.OperationalError:
                pass


            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar a tabela: {e}")
        finally:
            conn.close()