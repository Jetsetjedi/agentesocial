from tkinter import *
from tkinter import messagebox
import os
from negocio import Negocio  # Importa a lógica de negócios
from whatsbot import WhatsAppBot

class Application:
    def __init__(self, master=None):
        self.master = master  # Atribuir o parâmetro master ao atributo self.master
        self.whatsapp_bot = None 
        
        icon_path = os.path.join("assets", "logo.png")  # Caminho relativo para o ícone
        self.icon = PhotoImage(file=icon_path)  # Carregar o ícone
        self.master.iconphoto(True, self.icon)  # Definir o ícone da janela  

        self.master.resizable(False, False)  # Impede redimensionamento horizontal e vertical
        
        self.fontePadrao = ("Arial", "10")
        self.primeiroContainer = Frame(master)
        self.primeiroContainer["pady"] = 10
        self.primeiroContainer.pack()

        self.segundoContainer = Frame(master)
        self.segundoContainer["padx"] = 20
        self.segundoContainer.pack()

        self.terceiroContainer = Frame(master)
        self.terceiroContainer["padx"] = 20
        self.terceiroContainer.pack()

        self.quartoContainer = Frame(master)
        self.quartoContainer["pady"] = 20
        self.quartoContainer.pack()

        self.titulo = Label(self.primeiroContainer, text="Dados do usuário")
        self.titulo["font"] = ("Arial", "10", "bold")
        self.titulo.pack()

        self.nomeLabel = Label(self.segundoContainer,text="Nome", font=self.fontePadrao)
        self.nomeLabel.pack(side=LEFT)

        self.nome = Entry(self.segundoContainer)
        self.nome["width"] = 30
        self.nome["font"] = self.fontePadrao
        self.nome.pack(side=LEFT)

        self.senhaLabel = Label(self.terceiroContainer, text="Senha", font=self.fontePadrao)
        self.senhaLabel.pack(side=LEFT)

        self.senha = Entry(self.terceiroContainer)
        self.senha["width"] = 30
        self.senha["font"] = self.fontePadrao
        self.senha["show"] = "*"
        self.senha.pack(side=LEFT)

        self.autenticar = Button(self.quartoContainer)
        self.autenticar["text"] = "Autenticar"
        self.autenticar["font"] = ("Calibri", "8")
        self.autenticar["width"] = 12
        self.autenticar["command"] = self.verifica_senha
        self.autenticar.pack()

        self.mensagem = Label(self.quartoContainer, text="", font=self.fontePadrao)
        self.mensagem.pack()

        # Centralizar a janela no desktop
        self.centralizar_janela(master, 400, 300)

    def centralizar_janela(self, janela, largura, altura):
        """Centraliza a janela no desktop."""
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    #Método verificar senha
    def verifica_senha(self):
        """Verifica as credenciais do usuário."""
        usuario = self.nome.get()
        senha = self.senha.get()

        negocio = Negocio()  # Instancia a classe de negócios
        autenticado = negocio.autenticar_usuario(usuario, senha)

        if autenticado:
            self.mensagem["text"] = "Autenticado"
            # Abrir outra janela para as opções
            self.abrir_opcoes()
            # Fechar janela atual
            self.master.withdraw()
            self.limpar_campos()
        else:
            self.exibir_mensagem()
            self.limpar_campos()
    
    
   # Função que será chamada ao clicar no botão
    def exibir_mensagem(self):
        messagebox.showerror("Erro", "Usuario não Autenticado!")
   
   
    def abrir_opcoes(self):
        # Criar uma nova janela
        opcoes_janela = Toplevel()
        icon_path = os.path.join("assets", "logo.png")  # Caminho relativo para o ícone
        opcoes_janela.icon = PhotoImage(file=icon_path)  # Carregar o ícone
        opcoes_janela.iconphoto(True, self.icon)  # Definir o ícone da janela
        opcoes_janela.resizable(False, False)  # Impede redimensionamento horizontal e vertical
         
        opcoes_janela.title("Opções")
        self.centralizar_janela(opcoes_janela, 400, 300)

        # Criar o menu para a nova janela
        menu_opcoes = Menu(opcoes_janela)
        opcoes_janela.config(menu=menu_opcoes)

        # Menu Arquivo
        menu_arquivo = Menu(menu_opcoes, tearoff=0)
        menu_arquivo.add_command(label="Configuração", command=self.funcao_salvar_configuracao)
        menu_arquivo.add_command(label="Desconectar Whatsapp", command=self.desconectar_whatsapp)
        menu_arquivo.add_command(label="Fechar", command=lambda: self.fechar_opcoes(opcoes_janela))        
        menu_opcoes.add_cascade(label="Arquivo", menu=menu_arquivo)

        # Menu Ajuda
        menu_ajuda = Menu(menu_opcoes, tearoff=0)
        menu_ajuda.add_command(label="Sobre", command=self.funcao_sobre)
        menu_opcoes.add_cascade(label="Ajuda", menu=menu_ajuda)

        # Botão 1
        self.botao_whatsapp = Button(opcoes_janela, text="Conexão Whatsapp", font=self.fontePadrao, command=self.whastapp_conection)
        self.botao_whatsapp.pack(pady=10)

        # Botão 2
        botao2 = Button(opcoes_janela, text="Conexão Instagran", font=self.fontePadrao, command=self.instagra_conection)
        botao2.pack(pady=10)

        # Configurar para reexibir a janela de autenticação ao fechar a janela de opções
        opcoes_janela.protocol("WM_DELETE_WINDOW", lambda: self.fechar_opcoes(opcoes_janela))
    
    def whastapp_conection(self):
        """ Lógica para abrir o browser com whatsapp"""
        abrir_zap = Toplevel()
        abrir_zap.title("Monitorar Mensagens")
        self.centralizar_janela(abrir_zap,400,200)

        
       # Label para instrução
        Label(
            abrir_zap,
            text="Selecione um contato para monitorar mensagens recebidas:",
            font=self.fontePadrao
        ).pack(pady=5)

        # Frame para Listbox e Scrollbar
        frame_listbox = Frame(abrir_zap)
        frame_listbox.pack(pady=5)

        # Scrollbar para o Listbox
        scrollbar = Scrollbar(frame_listbox)
        scrollbar.pack(side="right", fill="y")

        # Listbox para exibir os contatos
        listbox = Listbox(frame_listbox, width=20, height=1, font=self.fontePadrao, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both")
        scrollbar.config(command=listbox.yview)

        # Buscar contatos no banco de dados e preencher o Listbox
        contatos = self.obter_contatos()  # Busca os contatos no banco
        for contato in contatos:
            listbox.insert(END, contato[0])  # Adiciona o nome do contato no Listbox

        # Botão para iniciar o monitoramento
        Button(
            abrir_zap,
            text="Abrir",
            font=self.fontePadrao,
            command=lambda: self.chamarwhats(listbox.get(listbox.curselection()), abrir_zap)
        ).pack(pady=10)

    # Buscar contatos no banco de dados
    def obter_contatos(self):
        """Obtem os contatos cadastrados no sistema"""
        instcontatos = Negocio()
        contatos = instcontatos.lista_cadastrada()
        return contatos 


    def instagra_conection(self):
        # Lógica para a Opção 2
        print("chamar regra de negocio 2")

    def fechar_opcoes(self, opcoes_janela):
            """Fecha a janela de opções e reexibe a janela de autenticação."""
            desconecta = WhatsAppBot()
            desconecta.desconectar()
            opcoes_janela.destroy()
            self.master.deiconify()
            
            
    
    def desconectar_whatsapp(self):
        """Desconecta do WhatsApp Web e reseta o botão."""
        desconecta = WhatsAppBot()
        desconecta.verificar_conexao()
        if desconecta:
            # Volta o botão ao estado original
            desconecta.desconectar()
            self.botao_whatsapp.config(bg="SystemButtonFace", text="Conexão Whatsapp")
            messagebox.showinfo("Desconectado", "WhatsApp foi desconectado com sucesso.")
        else:
            messagebox.showerror("Caracas", "Você não esta conectado, porque fazer isso?")

    def limpar_campos(self):
        """Limpa os campos de entrada."""
        self.nome.delete(0, END)  # Limpa o campo de nome
        self.senha.delete(0, END)  # Limpa o campo de senha
        self.mensagem["text"] = ""  # Limpa a mensagem exibida

    def funcao_salvar_configuracao(self):
        """Abre uma janela para salvar as configurações de conexão."""
        configuracao_janela = Toplevel()
        configuracao_janela.title("Configuração de Conexão")
        self.centralizar_janela(configuracao_janela, 400, 300)

        # Label e campo de entrada para o nome ou número do WhatsApp
        Label(configuracao_janela, text="Nome ou número do WhatsApp:", font=self.fontePadrao).pack(pady=5)
        usuario_entry = Entry(configuracao_janela, width=30, font=self.fontePadrao)
        usuario_entry.pack(pady=5)

        # Botão para salvar as configurações
        Button(
            configuracao_janela,
            text="Salvar",
            font=self.fontePadrao,
            command=lambda: self.salvar_configuracao(usuario_entry.get(), configuracao_janela)
        ).pack(pady=10)

    def salvar_configuracao(self, usuario, janela):
        """Salva as configurações no banco de dados."""
        if not usuario :
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        negocio = Negocio()
        sucesso = negocio.salvar_configuracao(usuario)

        if sucesso:
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            janela.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao salvar as configurações.")
    
    
    #Click Botão para iniciar o monitoramento
    def chamarwhats(self, usuario, janela):
        """Chama o browser e abre o whatsapp """
        if not usuario:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        #verificar se ja esta aberto a janela com o sistema Whatsapp
        verwhats = WhatsAppBot()
        vaberto = verwhats.verificar_conexao()
        if vaberto:
              whatsnegocio = Negocio()
              abertook = whatsnegocio.whastapp_conection(usuario)
              if abertook:
                    messagebox.showinfo("Sucesso", "Usuario enviado com Sucesso")
                    # Alterar a cor e o texto do botão que chamou esta função
                    self.botao_whatsapp.config(bg="green", text="Conectado")
                    janela.destroy()
        else:
            messagebox.showwarning("Alerta", "Whatsapp não sincronizado!")
            bot = WhatsAppBot()
            bot.iniciar_driver()
            bot.conectar_whatsapp()
            bot.verificar_conexao()
            if bot:
                print("agora esta aberto essa jossa mano.... vai não para")
                whatsnegocio = Negocio()
                abertook = whatsnegocio.whastapp_conection(usuario)
                if abertook:
                    messagebox.showinfo("Sucesso", "Usuario enviado com Sucesso")
                    self.botao_whatsapp.config(bg="green", text="Conectado")
                    janela.destroy()

    def funcao_sobre(self):
        messagebox.showinfo("Sobre", "Criar interface para digitar texto sobre o sistema")