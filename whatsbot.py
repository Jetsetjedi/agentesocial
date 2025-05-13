from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class WhatsAppBot:
    def __init__(self):
        self.driver = None

    def iniciar_driver(self):
        """Inicializa o WebDriver e armazena no objeto."""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def conectar_whatsapp(self):
        """Abre o WhatsApp Web e aguarda o QR Code ser escaneado."""
        self.driver.get("https://web.whatsapp.com/")
        print("Por favor, escaneie o QR Code para conectar ao WhatsApp Web.")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Lista de conversas']"))
        )
        print("Conexão estabelecida!")
        

    def verificar_conexao(self):
        """Verifica se o WhatsApp Web já está conectado."""
        try:
            WebDriverWait(self.driver, 10).until(
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
        


# Exemplo de uso
# bot = WhatsAppBot()
# bot.iniciar_driver()
# bot.conectar_whatsapp()