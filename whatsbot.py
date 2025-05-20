from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
import threading
import time
from negocio import Negocio

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.monitor_on_of = None
        self.ultimo_texto_processado = {}  # contato: texto
        self.negocio = Negocio()
        self.atendimentos = self.negocio.carregar_atendimentos()  # <-- agora carrega do banco!

    def iniciar_driver(self):
        """Inicializa o WebDriver e armazena no objeto."""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def conectar_whatsapp(self):
        """Abre o WhatsApp Web e aguarda o QR Code ser escaneado."""
        self.driver.get("https://web.whatsapp.com/")
        print("Por favor, escaneie o QR Code para conectar ao WhatsApp Web.")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Lista de conversas']"))
        )
        print("Conexão estabelecida!")
        

    def verificar_conexao(self):
        """Verifica se o WhatsApp Web já está conectado."""
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Lista de conversas']"))
            )
            print("WhatsApp Web já está conectado.")
            return True
        except Exception:
            print("WhatsApp Web não está conectado.")
            return False
    
    def desconectar(self):
        """Fecha o WebDriver e encerra a sessão do WhatsApp Web."""
        if self.driver:
           self.driver.quit()
           self.driver = None
           print("Desconectado do WhatsApp Web.")

    def enviar_mensagem(self, usuario, mensagem):
        # Exemplo básico: você precisa adaptar para buscar o contato e enviar a mensagem
        search_box = self.driver.find_element("xpath", "//div[@contenteditable='true'][@data-tab='3']")
        search_box.clear()
        search_box.send_keys(usuario)
        search_box.send_keys(u'\ue007')  # Pressiona Enter

        # Aguarda o chat abrir e envia a mensagem
        input_box = self.driver.find_element("xpath", "//div[@contenteditable='true'][@data-tab='10']")
        input_box.send_keys(mensagem)
        input_box.send_keys(u'\ue007')  # Pressiona Enter
    
    def iniciar_monitoramento(self, usuario, get_monitor_status):
        """Inicia o monitoramento em uma thread separada."""
        self.monitorando = True
        self.monitor_thread = threading.Thread(
            target=self._monitorar_mensagens_loop,
            args=(usuario, get_monitor_status),
            daemon=True
        )
        self.monitor_thread.start()

    def _monitorar_mensagens_loop(self, usuario, get_monitor_status):
        """Loop de monitoramento enquanto o status for 'on'."""
        print("Monitoramento iniciado.")
        while get_monitor_status() == "on":
            # Aqui você coloca a lógica de monitoramento real
            print(f"Monitorando mensagens para {usuario}...")
            
            messages = self.obter_ultimas_mensagens()
            if self.processar_mensagens(messages):
                print("Menu de vendas será implementado em breve.")            
            time.sleep(10)  # Simula o monitoramento periódico
        print("Monitoramento parado.")   



    def obter_ultimas_mensagens(self, limite=10):
        """Obtém as últimas mensagens da lista de conversas."""
        try:
            conversation_list = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Lista de conversas']"))
            )
            messages = conversation_list.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            return messages[0:limite] if len(messages) > limite else messages
        except Exception as e:
            print(f"Erro ao obter mensagens: {e}")
            return [] 

    def processar_mensagens(self, messages):
        """Processa as mensagens e executa ações específicas."""
        for message in messages:
            try:
                contato = message.find_element(By.CSS_SELECTOR, "span[dir='auto']").text
                dados = message.find_element(By.CSS_SELECTOR, "div._ak8k").text.strip()
                
                # Limpeza do texto
                if ":" in dados:
                    dados_limpo = dados.split(":")[-1].strip()
                else:
                    dados_limpo = dados.strip()
                if "\n" in dados_limpo:
                    dados_limpo = dados_limpo.split("\n")[-1].strip()

                #print(f"DEBUG: dados='{dados}' | dados_limpo='{dados_limpo}'")

                # Só processa se for uma mensagem nova
                if self.ultimo_texto_processado.get(contato) == dados:
                    continue  # Já processou essa mensagem

                print(f"Contato: {contato} | ÚltimaMSG: {dados}")

                # Atualiza o último texto processado
                self.ultimo_texto_processado[contato] = dados

                # Se contato não está em atendimento e mandou "start"
                if contato not in self.atendimentos and "start" in dados.lower():
                    self.atendimentos[contato] = "menu_categorias"
                    self.negocio.salvar_atendimento(contato, "menu_categorias")
                    self.template_boas_vindas(contato)
                    time.sleep(2)
                    self.enviar_menu_categorias(contato)
                    continue

                # Se contato está aguardando escolha de categoria
                if self.atendimentos.get(contato) == "menu_categorias":
                    if dados_limpo.isdigit():
                        categoria_idx = int(dados_limpo)
                        categorias = self.obter_categorias()
                        if 1 <= categoria_idx <= len(categorias):
                            categoria_escolhida = categorias[categoria_idx - 1]
                            self.atendimentos[contato] = ("menu_produtos", categoria_escolhida)
                            self.negocio.salvar_atendimento(contato, "menu_produtos", categoria_escolhida)
                            self.enviar_menu_produtos(contato, categoria_escolhida)
                        else:
                            self.enviar_mensagem(contato, "_Opção inválida. Por favor, escolha uma categoria válida._")
                    else:
                        self.enviar_mensagem(contato, "_Por favor, envie apenas o número da categoria desejada._")
                    continue

                # Se contato está aguardando escolha de produto
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "menu_produtos":
                    categoria_escolhida = self.atendimentos[contato][1]
                    produtos = self.obter_produtos_por_categoria_(categoria_escolhida)
                    if dados_limpo.isdigit():
                        produto_idx = int(dados_limpo)
                        if 1 <= produto_idx <= len(produtos):
                            produto_escolhido = produtos[produto_idx - 1]
                            self.atendimentos[contato] = ("confirmar_produto", categoria_escolhida, produto_escolhido)
                            self.negocio.salvar_atendimento(contato, "confirmar_produto", categoria_escolhida, produto_escolhido)
                            self.enviar_mensagem(contato, f"_Você escolheu:_*{produto_escolhido}*.\n Deseja finalizar o pedido? *(sim/não)*")
                        else:
                            self.enviar_mensagem(contato, "_Opção inválida. Por favor, escolha um produto válido._")
                    elif dados_limpo.lower() == "voltar":
                        self.atendimentos[contato] = "menu_categorias"
                        self.negocio.salvar_atendimento(contato, "menu_categorias")
                        self.enviar_menu_categorias(contato)
                    else:
                        self.enviar_mensagem(contato, "_Por favor, envie apenas o número do produto ou *'voltar'*._")
                    continue

                # Confirmação do produto
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "confirmar_produto":
                    _, categoria_escolhida, produto_escolhido = self.atendimentos[contato]
                    if dados_limpo.lower() == "sim":
                        self.atendimentos[contato] = ("coletar_endereco", categoria_escolhida, produto_escolhido)
                        self.negocio.salvar_atendimento(contato, "coletar_endereco", categoria_escolhida, produto_escolhido)
                        self.enviar_mensagem(contato, "Por favor, informe seu endereço para entrega:")
                    elif dados_limpo.lower() == "não":
                        self.atendimentos[contato] = "menu_categorias"
                        self.negocio.salvar_atendimento(contato, "menu_categorias")
                        self.enviar_menu_categorias(contato)
                    else:
                        self.enviar_mensagem(contato, "Responda apenas com '*sim*' ou '*não*'.")
                    continue

                # Coleta endereço e finaliza pedido
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_endereco":
                    _, categoria_escolhida, produto_escolhido = self.atendimentos[contato]
                    endereco = dados_limpo
                    self.negocio.registrar_pedido(contato, categoria_escolhida, produto_escolhido, endereco)
                    self.enviar_mensagem(contato, "*Pedido registrado! Em breve entraremos em contato para confirmar.*")
                    self.atendimentos.pop(contato)
                    self.negocio.salvar_atendimento(contato, "finalizado")
                    continue

            except StaleElementReferenceException:
                print("Elemento ficou stale, pulando para o próximo.")
                continue

            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                continue  # Pula para o próximo elemento
        return False
    
    # mensagem do menu das categorias
    def enviar_menu_categorias(self, contato):
        categorias = self.obter_categorias()
        menu = "*Menu de Categorias*\n\n"
        for idx, cat in enumerate(categorias, 1):
            menu += f"*{idx}* . _{cat}_\n"
        menu += "\n*_Digite o número da categoria desejada para ver os produtos._*"
        self.enviar_mensagem(contato, menu)

    # mensagem de boas vindas ao detectar start
    def template_boas_vindas(self, contato):
        msg = (
            f"*Bem-vindo {contato} ao atendimento automático!*\n\n"
            "A palavra *start* inicia um atendimento virtual para venda de qualquer coisa."
        )
        self.enviar_mensagem(contato, msg)

    # mensagem do menu dos produtos
    def enviar_menu_produtos(self, contato, categoria):
        produtos = self.obter_produtos_por_categoria(categoria)
        menu = f"*Produtos da categoria:* _{categoria}_:\n"
        for idx, prod in enumerate(produtos, 1):
            nome = prod[0]
            observacao = prod[1]
            valor = prod[2]
            menu += f"*{idx}* - _{nome}_\n"
            menu += f"  *Observação:* _{observacao}_\n"
            menu += f"  *Valor:* _R$_ _{valor:.2f}_\n"
        menu += "_Digite o número do produto desejado ou 'voltar' para escolher outra categoria._"
        self.enviar_mensagem(contato, menu)


    #Obtem as categorias para listar
    def obter_categorias(self):
        # Busca categorias do banco e retorna uma lista de nomes
        categorias = self.negocio.lista_categorias()
        return [cat[0] for cat in categorias]  # Ajuste conforme o retorno do seu método
    
    #Obtem os produtos da categoria para listar para o usuario...!!!???
    def obter_produtos_por_categoria(self, categoria_nome):
        # Busca produtos do banco pela categoria e retorna uma lista de nomes
        produtos = self.negocio.lista_produtos_por_categoria_completo(categoria_nome)
        return  produtos  # Ajuste conforme o retorno do seu método
    
    #Obtem os produtos da categoria para gragar somente o produto
    def obter_produtos_por_categoria_(self, categoria_nome):
        # Busca produtos do banco pela categoria e retorna uma lista de nomes
        produtos = self.negocio.lista_produtos_por_categoria(categoria_nome)
        return [prod[0] for prod in produtos ] # Ajuste conforme o retorno do seu método