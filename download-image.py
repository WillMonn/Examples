import requests
from requests.auth import HTTPDigestAuth
import http.client

url = "http://10.1.45.36/cgi-bin/mediaFileFind.cgi?action=factory.create"
username = "admin"
password = "Intelbras1"

# Inicialmente, você pode usar um valor vazio para o sessionID
session_id = ""
max_requests = 1  # Número máximo de requisições

for _ in range(max_requests):
    # Realizar a autenticação digest
    auth = HTTPDigestAuth(username, password)
    
    # Cabeçalhos, incluindo o sessionID se estiver disponível
    headers = {}
    if session_id:
        headers['Cookie'] = f'WebClientSessionID={session_id}'
    
    response = requests.get(url, headers=headers, auth=auth)
    
    if response.status_code == 200:
           
        # Extrair o valor após o "=" na resposta
        response_content = response.text.split('=')[1].strip()
        print("1ª Consulta:", response_content)
        
        # Atualizar o sessionID com o novo valor do cookie, se disponível
        new_session_id = response.cookies.get('WebClientSessionID')
        if new_session_id:
            print("Novo Cookie:", new_session_id)
            session_id = new_session_id
            
        # Segunda requisição com o valor obtido da primeira requisição
        second_url = f"http://10.1.45.36/cgi-bin/mediaFileFind.cgi?action=findFile&object={response_content}&condition.Channel=1&condition.StartTime=2023-08-16%2000:00:00&condition.EndTime=2023-08-16%2023:00:00&condition.Types[0]=jpg&condition.Flags[0]=Event&condition.Events[0]=FaceDetection&condition.DB.FaceDetectionRecordFilter.ImageType=GlobalSence"
        
        second_response = requests.get(second_url, headers=headers, auth=auth)
        if second_response.status_code == 200:
            print("2ª Consulta", second_response.text)

            # Terceira requisição usando o valor obtido da segunda resposta
            third_url = f"http://10.1.45.36/cgi-bin/mediaFileFind.cgi?action=findNextFile&object={response_content}&count=3"
            
            third_response = requests.get(third_url, headers=headers, auth=auth)
            if third_response.status_code == 200:
                print("3ª Consulta", third_response.text)
            else:
                print("Erro na terceira requisição. Código de status:", third_response.status_code)
                print("Resposta:")
                print(third_response.text)
        else:
            print("Erro na segunda requisição. Código de status:", second_response.status_code)
            print("Resposta:")
            print(second_response.text)
    else:
        print("Erro na requisição. Código de status:", response.status_code)
        print("Resposta:")
        print(response.text)

# Processar as linhas do resultado da terceira consulta
linhas = third_response.text.split("\n")
for i, linha in enumerate(linhas):
    if linha.startswith("items[") and "FilePath=" in linha:
        arquivo_parte = linha.split("FilePath=")[1].strip()
        print(arquivo_parte)

        conn = http.client.HTTPConnection("10.1.45.36")
        
        headers = {
            'Cookie': f'WebClientSessionID={new_session_id}'
        }

        image_path = f"{arquivo_parte}"
        print(image_path)

        conn.request("GET", image_path, headers=headers)
        res = conn.getresponse()

        if res.status == 200:
            image_data = res.read()

            # Crie um nome de arquivo único com base na iteração do loop
            nome_arquivo = f'image_{i}.jpg'

            # Salve a imagem em um arquivo local
            with open(nome_arquivo, 'wb') as f:
                f.write(image_data)

            print("Imagem salva com sucesso:", nome_arquivo)
        else:
            print(f"Erro ao obter a imagem: {res.status} {res.reason}")

        conn.close()

    