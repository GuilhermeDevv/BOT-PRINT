import json
from collections    import namedtuple
from utils.neocript import NeoCript
 
class ConfigReader:

    def read_json_config(filename, encrypt = False):
        try:
            # Realiza a leitura do arquivo
            file = open(filename)

            # Pega os dados
            data = file.read()

            # Cria o objeto
            obj = []

            # Caso os dados estejam criptogradados
            if encrypt:      
                # Cria um objeto personalizado
                obj = json.loads(data, object_hook =
                            lambda d : namedtuple('X', d.keys())
                            (*NeoCript.decrypt_values(d)))
            else: 

                # Cria um objeto personalizado
                obj = json.loads(data, object_hook =
                            lambda d : namedtuple('X', d.keys())
                            (*d.values()))
    
            # Retorna o objeto
            return obj  
        
        except Exception as e:
            # Retorna o objeto vazio
            return []

