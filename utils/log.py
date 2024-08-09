from datetime import date, datetime
import os

class Logger:

    # Metodo de criação da classe
    def __init__(self, output = False, directory = "./_log/"):

        # Seta as propriedades padrão
        self.output     = output
        self.directory  = directory
    
    def write_log(self, text):
       
        # Monta o nome do arquivo
        filename = f"{self.return_getdate().strftime('%Y_%m_%d')}.log"
        
        try:
            
            # Força a criação do diretório
            os.makedirs(self.directory, exist_ok=True)

            # Monta o caminho do arquivo
            file_path = os.path.join(self.directory, filename)
        
            # Abre o arquivo em modo de escrita (cria um novo arquivo ou sobrescreve um existente)
            with open(file_path, 'w', encoding='utf-8') as arquivo:

                # Escreve no arquivo
                arquivo.write(text)
            
        except Exception as e:

            # Exibe a excessao
            print(str(e))


    # funcao para retornar a data atual
    def return_getdate(self):

        # combina as datas
        resultado = datetime.combine(date.today(), datetime.now().time())

        # retorna
        return resultado
    

    def print(self, text):

        # Monta o texto
        text_log = f"{self.return_getdate().strftime('%Y/%m/%d %H:%M:%S')} - {text}"
        
        # Caso esteja em modo de output 
        if self.output:            

            # Escreve o log em arquivo
            self.write_log(text_log)

        else:
            # Exibe o log em tela
             print(text_log)

