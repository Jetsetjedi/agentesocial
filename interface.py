from tkinter import *
from tkinter import messagebox
import os
from negocio import Negocio  # Importa a lógica de negócios
from whatsbot import WhatsAppBot

class Application:
    def __init__(self, master=None):
        self.master = master  # Atribuir o parâmetro master ao atributo self.master
        self.bot = None
        self.monitor_on_of = None 
        self.negocio = Negocio()
        
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
        menu_arquivo.add_command(label="Painel", command=self.abrir_dashboard)
        menu_arquivo.add_command(label="Fechar", command=lambda: self.fechar_opcoes(opcoes_janela))        
        menu_opcoes.add_cascade(label="Arquivo", menu=menu_arquivo)

        # Menu Ajuda
        menu_ajuda = Menu(menu_opcoes, tearoff=0)
        # menu_ajuda.add_command(label="Painel", command=self.abrir_dashboard)
        menu_ajuda.add_command(label="Sobre", command=self.funcao_sobre)
        menu_opcoes.add_cascade(label="Ajuda", menu=menu_ajuda)

        # Botão 1
        self.botao_whatsapp = Button(opcoes_janela, text="Conexão Whatsapp", font=self.fontePadrao, command=self.whastapp_conection)
        self.botao_whatsapp.pack(pady=10)

        # Botão 2
        botao2 = Button(opcoes_janela, text="Conexão Instagram", font=self.fontePadrao, command=self.instagra_conection)
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
        if self.bot:
            self.bot.desconectar()
            self.bot = None
        opcoes_janela.destroy()
        self.master.deiconify()
            
            
    
    def desconectar_whatsapp(self):
        """Desconecta do WhatsApp Web e reseta o botão."""
        if self.bot:
            # Volta o botão ao estado original
            self.bot.desconectar()
            self.bot = None

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
    
    #abrir o dashboard para operação do Whatsapp
    def abrir_dashboard(self):
        dashboard = Toplevel()
        dashboard.title("Painel")
        self.centralizar_janela(dashboard, 400, 300)

        # Menu do dashboard
        menu_dashboard = Menu(dashboard)
        dashboard.config(menu=menu_dashboard)

        # Menu Cadastro
        menu_cadastro = Menu(menu_dashboard, tearoff=0)
        menu_cadastro.add_command(label="Nova Categoria", command=lambda: self.abrir_cadastro_categoria(dashboard))
        menu_cadastro.add_command(label="Novo Produto", command=lambda: self.abrir_cadastro_produto(dashboard))
        menu_dashboard.add_cascade(label="Cadastro", menu=menu_cadastro)

        #Menu Operação
        menu_operacao  = Menu(menu_dashboard, tearoff=0)
        menu_operacao.add_command(label="ON monitor de Mensagens", command=self.liga_monitora_messages)
        menu_operacao.add_command(label="OFF monitor de Mensagens", command=self.desliga_monitora_messages)
        menu_dashboard.add_cascade(label="Operação", menu=menu_operacao)

        Button(dashboard, text="Ver Pedidos", font=self.fontePadrao, command=self.abrir_lista_pedidos).pack(pady=5)
        Button(dashboard, text="Ver Atendimentos", font=self.fontePadrao, command=self.abrir_lista_atendimentos).pack(pady=5)

        Label(dashboard, text=f"Usuário conectado: {self.usuario_conectado}", font=self.fontePadrao).pack(pady=5)
        Label(dashboard, text="Mensagem:", font=self.fontePadrao).pack(pady=5)
        mensagem_entry = Entry(dashboard, width=30, font=self.fontePadrao)
        mensagem_entry.pack(pady=5)

        Button(
            dashboard,
            text="Enviar Mensagem",
            font=self.fontePadrao,
            command=lambda: self.enviar_mensagem_dashboard(self.usuario_conectado, mensagem_entry.get())
        ).pack(pady=10)

    # Liga o monitoramento das mensagens
    def liga_monitora_messages(self):
        self.monitor_on_of = "on"
        if self.bot and self.usuario_conectado:
            # Passa uma função que retorna o status atual do monitor
            self.bot.iniciar_monitoramento(
                self.usuario_conectado,
                lambda: self.monitor_on_of
            )
        else:
            messagebox.showerror("Erro", "Conecte o WhatsApp e selecione um usuário antes de monitorar.")
    
    # Desliga o monitoramento das mensagens
    def desliga_monitora_messages(self):
        self.monitor_on_of = "off"
    
    #abre a tela de cadastro de categoria
    def abrir_cadastro_categoria(self, parent):
        janela_categoria = Toplevel(parent)
        janela_categoria.title("Nova Categoria")
        self.centralizar_janela(janela_categoria, 300, 150)

        Label(janela_categoria, text="Nome da Categoria:", font=self.fontePadrao).pack(pady=5)
        entry_categoria = Entry(janela_categoria, width=30, font=self.fontePadrao)
        entry_categoria.pack(pady=5)

        Button(
            janela_categoria,
            text="Salvar",
            font=self.fontePadrao,
            command=lambda: self.salvar_categoria(entry_categoria.get(), janela_categoria)
        ).pack(pady=10)

    #Abre a tela de cadastro de Produtos
    def abrir_cadastro_produto(self, parent):
        janela_produto = Toplevel(parent)
        janela_produto.title("Novo Produto")
        self.centralizar_janela(janela_produto, 300, 200)

        Label(janela_produto, text="Nome do Produto:", font=self.fontePadrao).pack(pady=5)
        entry_produto = Entry(janela_produto, width=30, font=self.fontePadrao)
        entry_produto.pack(pady=5)

        Label(janela_produto, text="Observaçoes:", font=self.fontePadrao).pack(pady=5)
        entry_observacao = Entry(janela_produto, width=30, font=self.fontePadrao)
        entry_observacao.pack(pady=5)

        Label(janela_produto, text="Valor de venda:", font=self.fontePadrao).pack(pady=5)
        entry_valor_venda = Entry(janela_produto,width=30, font=self.fontePadrao)
        entry_valor_venda.pack(pady=5)

       
        Label(janela_produto, text="Escolha uma categoria:", font=self.fontePadrao).pack(pady=5)
        # Aqui você pode buscar as categorias do banco e popular um OptionMenu ou Listbox
        categorias = self.obter_categorias()
        var_categoria = StringVar(janela_produto)
        if categorias:
            var_categoria.set(categorias[0])  # Seleciona a primeira categoria por padrão
        option_categoria = OptionMenu(janela_produto, var_categoria, *categorias)
        option_categoria.pack(pady=5)

        Button(
            janela_produto,
            text="Salvar",
            font=self.fontePadrao,
            command=lambda: self.salvar_produto(entry_produto.get(), entry_observacao.get(), entry_valor_venda.get(), var_categoria.get(), janela_produto)
        ).pack(pady=10)

    def obter_categorias(self):
        negocio = Negocio()
        categorias = negocio.lista_categorias()
        return [cat[0] for cat in categorias]  # Ajuste conforme o retorno do seu banco
    
    
    def salvar_categoria(self, nome_categoria, janela):
        if not nome_categoria:
            messagebox.showerror("Erro", "O nome da categoria é obrigatório!")
            return
        negocio = Negocio()
        sucesso = negocio.salvar_categoria(nome_categoria)
        if sucesso:
            messagebox.showinfo("Sucesso", "Categoria cadastrada com sucesso!")
            janela.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao cadastrar categoria.")



    def salvar_produto(self, nome_produto, observacao, valor_venda, categoria, janela):
        if not nome_produto or not categoria or not observacao or not valor_venda:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
       
       # Validação e conversão do valor de venda
        valor = valor_venda.strip()
        try:
            valor_float = float(valor.replace(',', '.'))  # Aceita vírgula ou ponto
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido para o preço!")
            return
       
       
        negocio = Negocio()
        sucesso = negocio.salvar_produto(nome_produto, observacao, valor_float, categoria)
        if sucesso:
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            janela.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao cadastrar produto.")
    
    def enviar_mensagem_dashboard(self, usuario, mensagem):
        if not usuario or not mensagem:
            messagebox.showerror("Erro", "Usuário e mensagem são obrigatórios!")
            return

        if not self.bot or not self.bot.verificar_conexao():
            messagebox.showerror("Erro", "WhatsApp não está conectado!")
            return

        try:
            self.bot.enviar_mensagem(usuario, mensagem)
            messagebox.showinfo("Sucesso", "Mensagem enviada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar mensagem: {e}")    


    #Click Botão para iniciar o monitoramento
    def chamarwhats(self, usuario, janela):
        if not usuario:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        if not self.bot:
            self.bot = WhatsAppBot()
            self.bot.iniciar_driver()
            self.bot.conectar_whatsapp()

        if self.bot.verificar_conexao():
            # ... lógica de envio ...
            self.usuario_conectado = usuario  # <-- GUARDA O USUÁRIO

            messagebox.showinfo("Sucesso", "Usuario enviado com Sucesso")
            self.botao_whatsapp.config(bg="green", text="Conectado")
            janela.destroy()
        else:
            messagebox.showwarning("Alerta", "Whatsapp não sincronizado!")

    def funcao_sobre(self):
        messagebox.showinfo("Sobre", "Criar interface para digitar texto sobre o sistema")
    

    def abrir_lista_pedidos(self):
        janela = Toplevel()
        janela.title("Lista de Pedidos")
        self.centralizar_janela(janela, 800, 400)
        pedidos = self.negocio.listar_pedidos()
        listbox = Listbox(janela, width=120, font=self.fontePadrao)
        for pedido in pedidos:
            listbox.insert(END, f"{pedido['data']} | {pedido['contato']} | {pedido['categoria']} | {pedido['produto']} | {pedido['endereco']}")
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)

    def abrir_lista_atendimentos(self):
        janela = Toplevel()
        janela.title("Histórico de Atendimentos")
        self.centralizar_janela(janela, 900, 400)
        atendimentos = self.negocio.listar_atendimentos()
        listbox = Listbox(janela, width=140, font=self.fontePadrao)
        for at in atendimentos:
            listbox.insert(END, f"{at['ultima_interacao']} | {at['contato']} | {at['estado']} | {at['categoria']} | {at['produto']} | {at['endereco']}")
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)