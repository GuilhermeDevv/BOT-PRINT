# imports
import os
import json
import pyodbc
import time as t
from datetime import date, datetime, timedelta
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.utils    import ConfigReader
from utils.log      import Logger

# variaveis de controle
DBG_MD      = True
INTERVALO   = 30

# Configurações do banco de dados
db_config = ConfigReader.read_json_config('./config/db.json', True)

# Configurações do aplicativo
app_config = ConfigReader.read_json_config('./config/app.json', True)


# Cria o logger
log = Logger(app_config.output_log, app_config.log_directory)

# Cria o bot
bot = telebot.TeleBot(app_config.bot_token, parse_mode=None)

# funcao para listar os alarmes
def lista_alarmes():
    
    try:
        # define o caminho do arquivo
        caminho = os.path.join(os.getcwd() , 'config\\alarmes.json')

        # le o json do arquivo
        with open(caminho, 'r',  encoding='utf-8') as f:
            dados = json.load(f)
    
    except Exception as e:
        
        # mensagem de erro
        log.print(f"A listagem dos alarmes apresentou problema: {str(e)}")

    # retorna 
    return dados

def envia_imagem(alarme):
    
    # Define o retorno como default
    retorno = False
    
    try:
        # Captura o chat_id
        chat_id = alarme["chatId"]	

        # Monta o nome do arquivo"
        caminho_arquivo = app_config.file_directory + "/" + alarme["arquivo"]

        # Envia a mensagem
        bot.send_photo(chat_id, photo=open(caminho_arquivo, "rb"))

        # Define o retorno com OK
        retorno = True
    except Exception as e:
        
        # mensagem de erro
        log.print(f"O envio da captura de tela apresentou problema: {str(e)}")

    # Retorna o valor final
    return retorno


# funcao para iniciar a thread
def envia_requisicao(alarme):

    try:
        # Caso seja mensagens de captura de tela de página
        if alarme["tipo"] == "pagina":
            
            # Realiza o disparo
            if envia_disparo_pagina(alarme):

                # Define o retorno como OK
                log.print(f"O disparo do alarme " + alarme["nome"] + "foi realizado.")
        

    except Exception as e:
        
        # mensagem de erro
        log.print(f"O envio da requisição apresentou problema: {str(e)}")


def captura_tela(alarme):

    # Define o retorno como default
    retorno = False
    
    try:
        # Captura a url
        url = alarme["url"]

        # Configura as opções do chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")

        # Configura o drive do selenium
        selenium_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=selenium_service, options=chrome_options)
        driver.maximize_window()
        
        # Navega até a url
        driver.get(url)

        # Espera a página carregar completamente
        t.sleep(alarme["tempoEspera"])
        
        # Monta o nome do arquivo"
        caminho_arquivo = app_config.file_directory + "/" + alarme["arquivo"]

        # Tira um print da página
        driver.save_screenshot(caminho_arquivo)

        # Fecha o driver do Selenium
        driver.quit()
        
        # Define o retorno com OK
        retorno = True

    except Exception as e:
        
        # mensagem de erro
        log.print(f"A captura de tela apresentou problema: {str(e)}")
    
    # Retorna o valor final
    return retorno

def envia_disparo_pagina(alarme):
    
    # Define o retorno como default
    retorno = False
    
    try:
        # Tenta capturar a tela do navegador
        if captura_tela(alarme):
        
            # Envia a mensagem via telegram
            retorno = envia_imagem(alarme)


        # Salva a execução no banco de dados
        salva_execucao(alarme, retorno)

    except Exception as e:
        
        # mensagem de erro
        log.print(f"O disparo de alarme de página apresentou problema: {str(e)}")


    # Retorna o valor final
    return retorno



def salva_execucao(alarme, resultado):
    
    # Define o retorno como default
    retorno = False

    try:
        # Monta o connection string
        conn_str = f'DRIVER={db_config.provider};SERVER={db_config.server};DATABASE={db_config.database};UID={db_config.username};PWD={db_config.password}'

        # Conecta ao banco e cria o cursor
        conn = pyodbc.connect(conn_str, autocommit=True)      
        qry  = conn.cursor()
        
        # Seta o parametros
        params = (alarme["nome"], resultado)
        
        # Monta a query
        sql = f'exec {db_config.procedure} ?, ?'
        
        # Executa 
        qry.execute(sql, (params))  

        # fecha o objeto
        qry.close()
        conn.close()

        # Retorna OK
        retorno = True
 
    except Exception as e:
        
        # mensagem de erro
        log.print(f"O salvamento da execução no banco dos dados apresentou problema: {str(e)}")
    
    # Emite o retorno
    return retorno


# funcao para iniciar o processo
def inicia_processo():

    # lista os alarmes
    alarmes = lista_alarmes()
        
    # sinaliza que o serviço está funcionando
    log.print(f"Serviço OK, iniciando os disparos...")

    # loop
    while True:

        # pega a data de agora
        agora = datetime.now()
        
        # percorre a lista de alarmes
        for alarme in alarmes:
            
            # varivel de controle
            autorizadoEnvio = False

            # captura as variaveis
            ultimoEnvio = alarme["ultimoEnvio"]
            horarioIni  = datetime.combine(date.today(), datetime.strptime(alarme["horarioIni"], "%H:%M").time())
            horarioFim  = datetime.combine(date.today(), datetime.strptime(alarme["horarioFim"], "%H:%M").time())
            intervalo   = int(alarme["intervalo"])

            # print(agora)
            # print(ultimoEnvio)
            # print(horarioIni)
            # print(horarioFim)
            # print(intervalo)

            # caso esteja dentro do prazo 
            if ((agora > horarioIni) and (agora < horarioFim)):

                # caso não tenha nenhum envio
                if (ultimoEnvio == ""):

                    # Calcula o tempo em minutos da hora de agora
                    tempoMinutos = int((agora - horarioIni).total_seconds() / 60)
                
                    # Verifica se estamos no próximo intervalo ou se falta algum tempo
                    proximoIntervalo = tempoMinutos % intervalo

            
                    # caso esterja dentro do intervalo, habilita o envio
                    if (proximoIntervalo == 0):
                                    
                        # autoriza o envio
                        autorizadoEnvio = True

                else:
                    
                    # define o proximo envio
                    proximoEnvio = ultimoEnvio + timedelta(minutes=intervalo)

                    # verifica se já estamos no proximo envio
                    if (proximoEnvio < agora):

                        # autoriza o envio
                        autorizadoEnvio = True


            # caso o proximo envio esteja autorizado
            if autorizadoEnvio == True:
                
                # inicia o alarme
                envia_requisicao(alarme)

                # atualiza a data do último envio
                alarme["ultimoEnvio"] = agora

            else :
                
                # sinaliza que o serviço está funcionando
                log.print(f"Serviço OK, "  + alarme["nome"] + " não autorizado.")
        
        
        # aguarda o intervalo
        t.sleep(INTERVALO)
        

# teste = bot.get_updates()
# for i in teste:
#     print(i)

# inicia o script
inicia_processo()