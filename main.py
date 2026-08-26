import os
import json
from google import genai
from playwright.sync_api import sync_playwright

def extrair_dados_com_ia(texto_anotacoes):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Chave GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Você é um assistente de inventário de TI. Extraia os itens de patrimônio do texto abaixo e retorne ESTRITAMENTE um JSON no formato de lista de objetos, sem blocos de código ou markdown adicional.
    
    Campos por objeto:
    - patrimonio (string com o número)
    - tipo (Desktop, Monitor, Impressora, Notebook, etc.)
    - marca (string ou vazio "" se não informado)
    - modelo (string ou vazio "" se não informado)
    - unidade (string correspondente)
    - setor (string correspondente)

    Texto bruto:
    {texto_anotacoes}
    """

    print("Processando anotações com o Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    
    texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(texto_limpo)

def preencher_sistema(lista_itens, url_sistema):
    print("Iniciando navegador para preenchimento...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url_sistema)

        for item in lista_itens:
            print(f"Cadastrando patrimônio: {item['patrimonio']}...")
            
            # Ajustar quando estiver no PC da empresa
            page.fill("input[name='patrimonio']", item['patrimonio'])
            
            if item['marca']:
                page.fill("input[name='marca']", item['marca'])
            if item['modelo']:
                page.fill("input[name='modelo']", item['modelo'])

            page.select_option("select[name='tipo']", label=item['tipo'])
            page.select_option("select[name='unidade']", label=item['unidade'])
            page.select_option("select[name='setor']", label=item['setor'])

            page.click("button#btn-salvar")
            page.wait_for_timeout(1000)

        print("Todos os equipamentos foram cadastrados com sucesso!")
        browser.close()

if __name__ == "__main__":
    caminho_arquivo = "anotacoes.txt"

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado!")
        print("Crie o arquivo 'anotacoes.txt' com suas anotações antes de rodar.")
        exit(1)

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        anotacoes_do_dia = f.read().strip()

    if not anotacoes_do_dia:
        print("Aviso: O arquivo 'anotacoes.txt' está vazio.")
        exit(0)

    print("Lendo anotações do arquivo 'anotacoes.txt'...")
    dados_processados = extrair_dados_com_ia(anotacoes_do_dia)
    print("Dados extraídos com sucesso:\n", json.dumps(dados_processados, indent=2, ensure_ascii=False))

    # Quando estiver na empresa, descomente a linha abaixo:
    # preencher_sistema(dados_processados, "http://url-do-sistema")