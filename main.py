import os
import re
from playwright.sync_api import sync_playwright

def parse_arquivo_patrimonio(caminho_arquivo):
    """
    Lê o arquivo TXT e organiza os itens respeitando os blocos de setores demarcados por '- - -'.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo '{caminho_arquivo}' não encontrado.")

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    setor_atual = None
    equipamentos = []

    for num_linha, linha in enumerate(linhas, start=1):
        texto = linha.strip()
        if not texto:
            continue

        # Detecta a troca de setor (ex: "Comercial - - -", "DP ---")
        if re.search(r"-\s*-\s*-", texto):
            setor_limpo = re.split(r"-\s*-\s*-", texto)[0].strip()
            setor_atual = setor_limpo
            continue

        # Processa o equipamento (ex: "Desktop - 1234")
        if "-" in texto:
            partes = texto.split("-", 1)
            nome_equip = partes[0].strip()
            codigo_patrimonio = partes[1].strip()

            if not setor_atual:
                print(f"[Aviso Linha {num_linha}] Equipamento '{texto}' ignorado: nenhum setor definido antes dele.")
                continue

            equipamentos.append({
                "setor": setor_atual,
                "nome": nome_equip,
                "codigo": codigo_patrimonio
            })

    return equipamentos

def cadastrar_equipamentos_no_sistema(lista_equipamentos, url_sistema, usuario, senha):
    print(f"Total de equipamentos para cadastrar: {len(lista_equipamentos)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 1. Login no Sistema
        print("Acessando sistema e efetuando login...")
        page.goto(url_sistema)
        page.fill("#email", usuario)
        page.fill("#senha", senha)
        page.click("body > div.login-container > div > form > button")
        page.wait_for_load_state("networkidle")

        # 2. Tratamento do Modal de Pendências (Fecha caso exista)
        try:
            btn_fechar_pendencias = page.locator("#modal-pendencias > div > div.portal-actions > button, #modal-pendencias button:has-text('Fechar')")
            if btn_fechar_pendencias.is_visible(timeout=3000):
                print("Modal de pendências detectado. Fechando...")
                btn_fechar_pendencias.click()
                page.wait_for_timeout(500)
        except Exception:
            pass  # Se não houver modal, continua normalmente

        # 3. Acesso ao Módulo de Chamados / TI
        print("Acessando o sistema de Chamados...")
        page.click("body > section > div > a.system-link.chamados > h2") 
        page.wait_for_load_state("networkidle")

        # 4. Navegação: Menu Equipamentos
        print("Navegando para Equipamentos...")
        page.click("#appSidebar > ul > li:nth-child(7) > a > span")  
        page.wait_for_load_state("networkidle")

        # 5. Loop de Cadastro
        for indice, item in enumerate(lista_equipamentos, start=1):
            print(f"[{indice}/{len(lista_equipamentos)}] Cadastrando: {item['nome']} (Cod: {item['codigo']}) no setor [{item['setor']}]...")

            # 5.1 Clica em "Novo Equipamento"
            page.click("#btnNovoEq")
            page.wait_for_timeout(500)

            # 5.2 Preenche Código e Nome
            page.fill("#eq_codigo", item["codigo"])
            page.fill("#eq_nome", item["nome"])
            page.wait_for_timeout(200)

            # 5.3 Seleciona Local / Cliente: "São Geraldo (Matriz)" via JavaScript direto
            page.evaluate("""() => {
                const selectLocal = document.querySelector('#eq_local');
                if (selectLocal) {
                    for (let opt of selectLocal.options) {
                        if (opt.text.includes('São Geraldo (Matriz)')) {
                            selectLocal.value = opt.value;
                            selectLocal.dispatchEvent(new Event('change', { bubbles: true }));
                            selectLocal.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                }
            }""")
            page.wait_for_timeout(400)

            # 5.4 Seleciona Setor via JavaScript direto
            setor_alvo = item["setor"]
            page.evaluate("""(setor) => {
                const selectSetor = document.querySelector('#eq_setor');
                if (selectSetor) {
                    for (let opt of selectSetor.options) {
                        if (opt.text.trim().toLowerCase() === setor.trim().toLowerCase()) {
                            selectSetor.value = opt.value;
                            selectSetor.dispatchEvent(new Event('change', { bubbles: true }));
                            selectSetor.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                }
            }""", setor_alvo)
            page.wait_for_timeout(400)

            # 5.5 Clica em Gravar
            page.click("#btnGravarEq")
            page.wait_for_timeout(1000)

        print("Todos os equipamentos foram cadastrados com sucesso!")
        browser.close()

if __name__ == "__main__":
    ARQUIVO_TXT = "anotacoes.txt"
    
    # URL e Credenciais
    URL_SISTEMA = "http://192.168.0.253"
    USUARIO = "yurijaciel2@gmail.com"
    SENHA = "180725"

    try:
        dados_processados = parse_arquivo_patrimonio(ARQUIVO_TXT)
        if not dados_processados:
            print("Nenhum registro válido encontrado para envio.")
            exit(0)

        cadastrar_equipamentos_no_sistema(dados_processados, URL_SISTEMA, USUARIO, SENHA)
    except Exception as e:
        print(f"Erro durante a execução: {e}")