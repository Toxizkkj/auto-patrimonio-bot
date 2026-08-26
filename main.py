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
    
    # Limpa possíveis marcações de markdown retornadas
    texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(texto_limpo)

def preencher_sistema(lista_itens, url_sistema):
    print("Iniciando navegador para preenchimento...")
    with sync_playwright() as p:
        # headless=False para você ver o robô preenchendo a tela
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url_sistema)

        for item in lista_itens:
            print(f"Cadastrando patrimônio: {item['patrimonio']}...")
            
            # --- AJUSTAR SELETORES QUANDO ESTIVER NO PC DA EMPRESA ---
            page.fill("input[name='patrimonio']", item['patrimonio'])
            
            if item['marca']:
                page.fill("input[name='marca']", item['marca'])
            if item['modelo']:
                page.fill("input[name='modelo']", item['modelo'])

            # Para campos do tipo Select / Dropdown
            page.select_option("select[name='tipo']", label=item['tipo'])
            page.select_option("select[name='unidade']", label=item['unidade'])
            page.select_option("select[name='setor']", label=item['setor'])

            # Botão de salvar
            page.click("button#btn-salvar")
            page.wait_for_timeout(1000) # Espera 1 segundo entre os cadastros

        print("Todos os equipamentos foram cadastrados com sucesso!")
        browser.close()

if __name__ == "__main__":
    # Exemplo de anotação rápida que você poderá passar
    anotacoes_exemplo = """
    patrimonio 4501 desktop dell optiplex setor ti unidade matriz,
    patrimonio 4502 monitor lg setor rh unidade filial,
    patrimonio 4503 impressora setor financeiro unidade matriz
    """
    
    # 1. Converte anotações em dados estruturados
    dados_processados = extrair_dados_com_ia(anotacoes_exemplo)
    print("Dados extraídos com sucesso:\n", json.dumps(dados_processados, indent=2, ensure_ascii=False))

    # 2. Quando estiver na empresa, descomente a linha abaixo e coloque a URL real do sistema:
    # preencher_sistema(dados_processados, "http://sistema-interno.suaempresa/patrimonio")
