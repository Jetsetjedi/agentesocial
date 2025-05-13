from tkinter import Tk
from interface import Application
from conexao.sqllite import inicializar_banco

if __name__ == "__main__":
    inicializar_banco()  # Inicializa o banco de dados
    root = Tk()
    root.title("Agente Social JS")
    app = Application(root)
    root.mainloop()