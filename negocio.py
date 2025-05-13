from conexao.banco import conexao
from conexao.sqllite import conexaosqllt

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


class Negocio:
    def __init__(self):
        pass
    
    #funcões GLOBAIS da Classe Negocio
    def autenticar_usuario(self, usuario, senha):
        """
        Autentica o usuário verificando as credenciais no banco de dados.
        Retorna True se autenticado, False caso contrário.
        """
        connection = conexao()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
                cursor.execute(query, (usuario, senha))
                resultado = cursor.fetchone()
                if resultado:
                    ret_senha = resultado[6]  # Supondo que a senha está na coluna 6
                    return ret_senha == senha
                return False
            except Exception as e:
                print(f"Erro ao autenticar usuário: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        else:
            print("Erro ao conectar ao banco de dados.")
            return False
    
    def salvar_configuracao(self, usuario):
        """Salva as configurações de conexão no banco de dados.
           Retorna True se bem-sucedido, False caso contrário.
        """
        connection = conexaosqllt()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO configuracoes (nome_no_whatsapp)
                    VALUES (?)
                """, (usuario,))
                connection.commit()
                return True
            except Exception as e:
                print(f"Erro ao salvar configurações: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        else:
            print("Erro ao conectar ao banco de dados.")
            return False
        

    def whastapp_conection(self,usuario):
        """ Lógica para Abrir o Whatsapp. """
        conectzap = conexaosqllt() 
        if conectzap:
            try:
                cursor = conectzap.cursor()
                query = "SELECT * FROM configuracoes WHERE nome_no_whatsapp = ?"
                cursor.execute(query, (usuario,))
                resultadowhats = cursor.fetchone()
                if resultadowhats:
                    ret_userwhats = resultadowhats[1]  # Supondo que a senha está na coluna 1                    
                    # return ret_userwhats == senha
                    print("Whatsapp pronto para monitorar. ",ret_userwhats)
                    # inicia_whatsapp(ret_userwhats)
                    return True
                
                return False #fim if resultado
            except Exception as e:
                print(f"Erro Na query o u cursor: {e}")
                return False
            finally:
                cursor.close()
                conectzap.close()
        else:
            print("Erro ao conectar ao banco de dados.")
            return False        

    def instagra_conection(self):
        """
        Lógica para a Opção 2.
        Exemplo: Realizar outra ação específica.
        """
        print("Executando a lógica da Opção 2 no negócio.")

    def lista_cadastrada(self):
        """Busca os usuarios cadastrados para monitoramento de converças locais"""
        connection = conexaosqllt()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT nome_no_whatsapp FROM configuracoes"
                cursor.execute(query)
                resultado = cursor.fetchall()
                if resultado:
                    return resultado
                return False
            except Exception as e:
                print(f"Erro ao autenticar usuário: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        else:
            print("Erro ao conectar ao banco de dados.")
            return False



#FUNÇÔES exclusivas da classe Negocio
def inicia_whatsapp(usuario):
    """
    Inicia o navegador e abre o WhatsApp Web, permitindo sincronização e monitoramento.
    """
    user = usuario
    print(f"Iniciando WhatsApp para o usuário: {user}")
    service = Service(ChromeDriverManager().install())
    nav = webdriver.Chrome(service=service)
    nav.get("https://web.whatsapp.com")

    # Esperar o usuário sincronizar o QR Code
    for tentativa in range(3):
        print(f"Tentativa {tentativa + 1} de 3 para sincronizar o QR Code...")
        time.sleep(30)  # Dá tempo para o usuário escanear o QR Code

        try:
            # Verifica se o QR Code foi escaneado (exemplo: procura por um elemento da interface principal)
            nav.find_element('xpath', '//*[@id="side"]')
            print("Sincronização bem-sucedida!")
            
            # Persistir estado de sincronização (exemplo: salvar no banco de dados)
            salvar_sincronizacao(usuario)
            break
          
        except NoSuchElementException:
            print("QR Code não escaneado. Tentando novamente...")
    else:
        print("Sincronização falhou após 3 tentativas. Abortando operação.")
        nav.quit()
        return False

    # Monitorar mensagens recebidas
    # monitorar_mensagens(nav,usuario)
    return True
    # Monotorar mensagens não lidas
    # monitorar_msg_no_read(nav)
    # return True


def salvar_sincronizacao(usuario):
    """
    Salva no banco de dados que o usuário sincronizou o WhatsApp Web.
    """
    connection = conexaosqllt()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE configuracoes
                SET sincronizado = 1
                WHERE nome_no_whatsapp = ?
            """, (usuario,))
            connection.commit()
            print("Estado de sincronização salvo com sucesso.")
        
        except Exception as e:
            print(f"Erro ao salvar sincronização: {e}")
        finally:
            cursor.close()
            connection.close()




    # Olhar para converças não lida e ficar olhando
    # //*[@id="pane-side"]/div
    

    
    
    
    
    # nav.find_element('xpath', '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p').send_keys(usuario)
    # nav.find_element('xpath', '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p').send_keys(Keys.ENTER)

# Monitora mensagens de teste local temporaria    
def monitorar_msg_no_read(nav):
    """ Monitora mensagens não lidas no WhatsApp Web e exibe um menu de resposta. """
    # Exemplo: Verificar novas mensagens
     # Clicar  em Não lidas  //*[@id="pane-side"]/div/div/div //*[@id="pane-side"]/div  
    nav.find_element('xpath', '//*[@id="all-filter"]').click()    
    while True:
        try:
             time.sleep(60)
            #   //*[@id="pane-side"]/div
             mensagens = nav.find_element('xpath', '//*[@id="pane-side"]') 
             if mensagens:                 
                #  print(f"Mensagens não lidas?: {mensagens.text}")
                 for mensagem in mensagens:
                        nome_contato = mensagens.find_element('xpath', './/span[contains(@class, "contact-name")]').text  # Nome do contato
                        print(f"Mensagens de?: {nome_contato}")

        except Exception as e:
            print(f"Erro ao monitorar mensagens: {e}")
            break
        

# Monitora mensagens de REAL ATENÇÂO local  
def monitorar_mensagens(nav, usuario):
    """Monitora mensagens recebidas no WhatsApp Web e exibe um menu de resposta para um usuario."""

    print(f"Iniciando monitoramento de mensagens para o usuário: {usuario}")
    
    # Aguarde o elemento da lista de conversas estar disponível
    conversation_list = WebDriverWait(nav, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Lista de conversas']"))
        )
    # Encontre as mensagens na lista
    messages = conversation_list.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    
    # Filtrar as últimas 10 mensagens
    last_10_messages = messages[0:] if len(messages) > 10 else messages

    # Iterar sobre as últimas 10 mensagens e imprimir o conteúdo
    for message in last_10_messages:
        try:
            
            # Extraia o texto da mensagem
            contato = message.find_element(By.CSS_SELECTOR, "span[dir='auto']").text
            time = message.find_element(By.CSS_SELECTOR, "div._ak8i").text
            dados = message.find_element(By.CSS_SELECTOR,"div._ak8k").text
            print(f"Horário: {time} - Contato: {contato}")
            print(f"UlmimaMSG: {dados}")                         
                 
            
        except Exception as e:
            print(f"Erro ao monitorar mensagens: {e}")
            break


def responder_mensagem(nav, mensagem):
    """Responde a uma mensagem recebida."""
    try:
        # mensagem.click()  # Clica na mensagem para abrir a conversa
        campo_resposta = nav.find_element('xpath', '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p')
        resposta = mensagem #input("Digite sua resposta: ")        
        
        campo_resposta.send_keys(resposta)
        campo_resposta.send_keys(Keys.ENTER)
        print("Mensagem enviada com sucesso.")
    except Exception as e:
        print(f"Erro ao responder mensagem: {e}")

        
        
