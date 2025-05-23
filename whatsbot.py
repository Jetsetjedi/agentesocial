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
        self.carrinhos = {}  # contato: lista de produtos (tuplas)
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
                    # ...dentro do bloco de escolha de produto...
                    if dados_limpo.isdigit():
                        produto_idx = int(dados_limpo)
                        if 1 <= produto_idx <= len(produtos):
                            produto_escolhido = produtos[produto_idx - 1]
                            # Novo estado: coletar quantidade
                            self.atendimentos[contato] = ("coletar_quantidade", categoria_escolhida, produto_escolhido)
                            self.enviar_mensagem(contato, f"Você escolheu: *{produto_escolhido}*.\nQual a quantidade desejada?")
                        else:
                            self.enviar_mensagem(contato, "_Opção inválida. Por favor, escolha um produto válido._")
                        continue
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

                # Coleta quantidade do produto
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_quantidade":
                    _, categoria_escolhida, produto_escolhido = self.atendimentos[contato]
                    if dados_limpo.isdigit() and int(dados_limpo) > 0:
                        quantidade = int(dados_limpo)
                        # Salva para confirmação
                        self.atendimentos[contato] = ("confirmar_produto", categoria_escolhida, produto_escolhido, quantidade)
                        self.enviar_mensagem(contato, f"Confirma a compra de *{quantidade}* unidade(s) de *{produto_escolhido}*? (sim/não)")
                    else:
                        self.enviar_mensagem(contato, "Por favor, informe uma quantidade válida (número maior que zero).")
                    continue                
                
                # Confirmação do produto
                # No fluxo de confirmação do produto:
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "confirmar_produto":
                    # Suporte tanto para 3 quanto 4 elementos (retrocompatível)
                    if len(self.atendimentos[contato]) == 4:
                        _, categoria_escolhida, produto_escolhido, quantidade = self.atendimentos[contato]
                    else:
                        _, categoria_escolhida, produto_escolhido = self.atendimentos[contato]
                        quantidade = 1  # padrão antigo

                    if dados_limpo.lower() == "sim":
                        produto_completo = self.negocio.buscar_produto_completo(produto_escolhido, categoria_escolhida)
                        if produto_completo:
                            # Adiciona ao carrinho como (nome, observacao, valor, quantidade)
                            if contato not in self.carrinhos:
                                self.carrinhos[contato] = []
                            nome, observacao, valor = produto_completo
                            self.carrinhos[contato].append((nome, observacao, valor, quantidade))
                            self.enviar_mensagem(contato, "Produto adicionado ao carrinho!\nDeseja continuar comprando? (sim para continuar, finalizar para encerrar o pedido)")
                            self.atendimentos[contato] = ("aguardando_continuar", categoria_escolhida)
                            self.negocio.salvar_atendimento(contato, "aguardando_continuar", categoria_escolhida)
                        else:
                            self.enviar_mensagem(contato, "Erro ao adicionar produto ao carrinho.")
                    elif dados_limpo.lower() == "não":
                        self.atendimentos[contato] = "menu_categorias"
                        self.negocio.salvar_atendimento(contato, "menu_categorias")
                        self.enviar_menu_categorias(contato)
                    else:
                        self.enviar_mensagem(contato, "Responda apenas com '*sim*' ou '*não*'.")
                    continue

                # Fluxo para continuar comprando
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "aguardando_continuar":
                    if dados_limpo.lower() == "sim":
                        self.atendimentos[contato] = "menu_categorias"
                        self.negocio.salvar_atendimento(contato, "menu_categorias")
                        self.enviar_menu_categorias(contato)
                    elif dados_limpo.lower() == "finalizar":
                        self.atendimentos[contato] = "coletar_dados_cliente"
                        self.negocio.salvar_atendimento(contato, "coletar_dados_cliente")
                        self.enviar_mensagem(contato, "Para finalizar, informe seu nome completo:")
                    else:
                        self.enviar_mensagem(contato, "Responda com 'sim' para continuar comprando ou 'finalizar' para encerrar o pedido.")
                    continue                
                
                # Coleta endereço e finaliza pedido
                if self.atendimentos.get(contato) == "coletar_dados_cliente":
                    nome_cliente = dados_limpo
                    self.atendimentos[contato] = ("coletar_cep", nome_cliente)
                    self.enviar_mensagem(contato, "Informe o CEP para entrega:")
                    continue

                # Novo bloco: coleta o CEP e consulta o endereço
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_cep":
                    nome_cliente = self.atendimentos[contato][1]
                    cep = dados_limpo.replace("-", "").strip()
                    endereco_info = self.negocio.buscaendereco(cep)
                    if endereco_info:
                        endereco_str = f"{endereco_info['logradouro']}, {endereco_info['bairro']}, {endereco_info['localidade']}-{endereco_info['uf']}"
                        self.atendimentos[contato] = ("confirmar_endereco", nome_cliente, cep, endereco_str)
                        self.enviar_mensagem(contato, f"Endereço encontrado:\n{endereco_str}\n\nEstá correto? (sim/não)")
                    else:
                        self.enviar_mensagem(contato, "CEP não encontrado ou inválido. Por favor, digite novamente:")
                    continue

                # Novo bloco: confirmação do endereço
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "confirmar_endereco":
                    nome_cliente = self.atendimentos[contato][1]
                    cep = self.atendimentos[contato][2]
                    endereco_str = self.atendimentos[contato][3]
                    if dados_limpo.lower() == "sim":
                        self.atendimentos[contato] = ("coletar_numero_complemento", nome_cliente, cep, endereco_str)
                        self.enviar_mensagem(contato, "Informe o número e complemento (ex: 123, apto 45):")
                    else:
                        self.atendimentos[contato] = ("coletar_cep", nome_cliente)
                        self.enviar_mensagem(contato, "Ok, digite o CEP novamente:")
                    continue

                # Novo bloco: coleta número e complemento
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_numero_complemento":
                    nome_cliente = self.atendimentos[contato][1]
                    cep = self.atendimentos[contato][2]
                    endereco_str = self.atendimentos[contato][3]
                    numero_complemento = dados_limpo
                    endereco_completo = f"{endereco_str}, {numero_complemento}, CEP: {cep}"
                    self.atendimentos[contato] = ("coletar_referencia", nome_cliente, endereco_completo)
                    self.enviar_mensagem(contato, "Informe um ponto de referência (ou digite '-' para ignorar):")
                    continue

                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_referencia":
                    nome_cliente = self.atendimentos[contato][1]
                    endereco = self.atendimentos[contato][2]
                    referencia = dados_limpo if dados_limpo != "-" else ""
                    # Agora finalize o pedido
                    produtos = self.carrinhos.get(contato, [])
                    resumo = "*Resumo do pedido:*\n"
                    total = 0
                    for idx, prod in enumerate(produtos, 1):
                        if len(prod) == 4:
                            nome, observacao, valor, quantidade = prod
                        else:
                            nome, observacao, valor = prod
                            quantidade = 1
                        subtotal = valor * quantidade
                        resumo += f"{idx}. {nome} - {observacao} - {quantidade}x R$ {valor:.2f} = R$ {subtotal:.2f}\n"
                        total += subtotal
                    resumo += f"\n*Total: R$ {total:.2f}*\n"
                    resumo += f"\nNome: {nome_cliente}\nEndereço: {endereco}\nReferência: {referencia}"
                    self.enviar_mensagem(contato, resumo)
                    self.enviar_mensagem(contato, "Deseja pagar agora pelo Mercado Pago? (sim/não)")
                    self.atendimentos[contato] = ("aguardando_pagamento", nome_cliente, endereco, referencia)
                    continue

                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "aguardando_pagamento":
                    # Recupere os dados do atendimento
                    _, nome_cliente, endereco, referencia = self.atendimentos[contato]
                    if dados_limpo.lower() == "sim":
                        self.atendimentos[contato] = ("coletar_dados_pagamento", nome_cliente, endereco, referencia)
                        self.enviar_mensagem(contato, "Informe seu CPF ou CNPJ:")
                        continue

                    elif dados_limpo.lower() == "não":
                        produtos = self.carrinhos.get(contato, [])
                        self.enviar_mensagem(contato, "*Pedido registrado! Em breve entraremos em contato para confirmar.*")
                        self.negocio.registrar_pedido(contato, produtos, nome_cliente, endereco, referencia)
                        self.atendimentos.pop(contato)
                        self.carrinhos.pop(contato, None)
                        self.negocio.salvar_atendimento(contato, "finalizado")
                        continue

                # Coleta CPF/CNPJ
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_dados_pagamento":
                    _, nome_cliente, endereco, referencia = self.atendimentos[contato]
                    documento = dados_limpo.strip()
                    if not documento or not documento.isdigit() or len(documento) not in [11, 14]:
                        self.enviar_mensagem(contato, "CPF ou CNPJ inválido. Por favor, digite apenas os números (11 para CPF, 14 para CNPJ):")
                        continue
                    self.atendimentos[contato] = ("coletar_email_pagamento", nome_cliente, endereco, referencia, documento)
                    self.enviar_mensagem(contato, "Informe seu e-mail para o pagamento:")
                    continue

                # Coleta e-mail
                if isinstance(self.atendimentos.get(contato), tuple) and self.atendimentos[contato][0] == "coletar_email_pagamento":
                    nome_cliente = self.atendimentos[contato][1]
                    endereco = self.atendimentos[contato][2]
                    referencia = self.atendimentos[contato][3]
                    documento = self.atendimentos[contato][4]
                    email = dados_limpo.strip()
                    if not email or "@" not in email or "." not in email:
                        self.enviar_mensagem(contato, "E-mail inválido. Por favor, digite um e-mail válido:")
                        continue
                    produtos = self.carrinhos.get(contato, [])
                    link_pagamento = self.negocio.gerar_link_pagamento(produtos, nome_cliente, email, documento, referencia, modo_sandbox=True)
                    self.enviar_mensagem(contato, f"Seu link de pagamento Mercado Pago:\n{link_pagamento}")
                    self.enviar_mensagem(contato, "*Pedido registrado! Assim que o pagamento for confirmado, entraremos em contato.*")
                    self.negocio.registrar_pedido(contato, produtos, nome_cliente, endereco, referencia)
                    self.atendimentos.pop(contato)
                    self.carrinhos.pop(contato, None)
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
            f"*Bem-vindo* _{contato}_ *ao atendimento automático!*\n\n"
            "A palavra *start* inicia um atendimento.\n\n"
            "_Empresa_: *Carros Em Destaque*.\n\n"
            "*Compre carro na palma da mão*\n\n"
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
            if valor == 0:
                continue  # Ignora produtos com valor 0
            menu += f"*{idx}* - _{nome}_\n"
            menu += f"  Observação: {observacao}\n"
            menu += f"  Valor: R$ {valor:.2f}\n"
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
    
    #Obtem os produtos da categoria para gravar somente o produto
    def obter_produtos_por_categoria_(self, categoria_nome):
        # Busca produtos do banco pela categoria e retorna uma lista de nomes
        produtos = self.negocio.lista_produtos_por_categoria(categoria_nome)
        return [prod[0] for prod in produtos ] # Ajuste conforme o retorno do seu método