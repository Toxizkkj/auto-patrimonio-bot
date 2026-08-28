import os
import re
from playwright.sync_api import sync_playwright

def parse_arquivo_patrimonio(caminho_arquivo):
    """
    Lê o arquivo TXT e organiza os itens respeitando:
    Setor - - -
    Nome - Patrimonio - Marca - Modelo
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

        # Detecta troca de setor (ex: "Comercial - - -", "DP ---")
        if re.search(r"-\s*-\s*-", texto):
            setor_limpo = re.split(r"-\s*-\s*-", texto)[0].strip()
            setor_atual = setor_limpo
            continue

        # Processa o equipamento com múltiplos campos separados por hífen
        if "-" in texto:
            partes = [p.strip() for p in texto.split("-")]
            
            nome_equip = partes[0] if len(partes) > 0 else ""
            codigo_patrimonio = partes[1] if len(partes) > 1 else ""
            marca_equip = partes[2] if len(partes) > 2 else ""
            modelo_equip = partes[3] if len(partes) > 3 else ""

            if not setor_atual:
                print(f"[Aviso Linha {num_linha}] Equipamento '{texto}' ignorado: nenhum setor definido antes dele.")
                continue

            equipamentos.append({
                "setor": setor_atual,
                "nome": nome_equip,
                "codigo": codigo_patrimonio,
                "marca": marca_equip,
                "modelo": modelo_equip
            })

    return equipamentos

def criar_novo_setor(page, nome_setor):
    """Fecha o modal de equipamento, adiciona o novo setor e fecha a listagem."""
    print(f"⚙️ Setor '{nome_setor}' não encontrado. Criando novo setor no sistema...")
    
    # 1. Fecha o modal de Novo Equipamento
    page.click("#btnFecharEq")
    page.wait_for_timeout(400)

    # 2. Clica em adicionar setor
    page.click("#btnAdicionarSetorEq")
    page.wait_for_timeout(500)

    # 3. Clica no botão de novo setor dentro do modal
    page.click("#btnNovoSetorEq")
    page.wait_for_timeout(400)

    # 4. Escreve o nome do setor
    page.fill("#setorNome", nome_setor)
    page.wait_for_timeout(200)

    # 5. Salva o setor
    page.click("#modalSetor > div.tec-modal-foot > button.btn.btn-success.tec-btn-sm")
    page.wait_for_timeout(800)

    # 6. Fecha a modal de lista de setores
    page.click("#modalListaSetores > div.tec-modal-foot > button")
    page.wait_for_timeout(500)
    print(f"✅ Setor '{nome_setor}' cadastrado com sucesso!")

def preencher_dados_formulario(page, item):
    """Preenche os campos de equipamento e seleciona cliente e setor via JS."""
    # Preenche Código, Nome, Marca e Modelo
    page.fill("#eq_codigo", item["codigo"])
    page.fill("#eq_nome", item["nome"])
    
    if item["marca"]:
        page.fill("#eq_marca", item["marca"])
    if item["modelo"]:
        page.fill("#eq_modelo", item["modelo"])
        
    page.wait_for_timeout(200)

    # Seleciona Local / Cliente fixo: "São Geraldo (Matriz)"
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
    page.wait_for_timeout(300)

    # Seleciona o Setor
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
    }""", item["setor"])
    page.wait_for_timeout(300)

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

        # 2. Fecha modal de Pendências se existir
        try:
            btn_fechar_pendencias = page.locator("#modal-pendencias > div > div.portal-actions > button, #modal-pendencias button:has-text('Fechar')")
            if btn_fechar_pendencias.is_visible(timeout=3000):
                print("Modal de pendências detectado. Fechando...")
                btn_fechar_pendencias.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

        # 3. Acesso ao Módulo de Chamados / TI
        print("Acessando o sistema de Chamados...")
        page.click("body > section > div > a.system-link.chamados > h2") 
        page.wait_for_load_state("networkidle")

        # 4. Navegação para Equipamentos
        print("Navegando para Equipamentos...")
        page.click("#appSidebar > ul > li:nth-child(7) > a > span")  
        page.wait_for_load_state("networkidle")

        # 5. Loop de Cadastro
        for indice, item in enumerate(lista_equipamentos, start=1):
            print(f"[{indice}/{len(lista_equipamentos)}] Processando: {item['nome']} (Cod: {item['codigo']}) - Setor: [{item['setor']}]...")

            # 5.1 Abre modal Novo Equipamento
            page.click("#btnNovoEq")
            page.wait_for_timeout(500)

            # 5.2 Verifica se o setor já existe nas opções do #eq_setor
            setor_existe = page.evaluate("""(setor) => {
                const selectSetor = document.querySelector('#eq_setor');
                if (!selectSetor) return false;
                for (let opt of selectSetor.options) {
                    if (opt.text.trim().toLowerCase() === setor.trim().toLowerCase()) {
                        return true;
                    }
                }
                return false;
            }""", item["setor"])

            # 5.3 Se não existir, executa o fluxo de criação de setor
            if not setor_existe:
                criar_novo_setor(page, item["setor"])
                # Reabre o modal de Novo Equipamento
                page.click("#btnNovoEq")
                page.wait_for_timeout(500)

            # 5.4 Preenche todos os campos
            preencher_dados_formulario(page, item)

            # 5.5 Clica em Gravar
            page.click("#btnGravarEq")
            page.wait_for_timeout(1000)

        print("Todos os equipamentos foram cadastrados com sucesso!")
        browser.close()

if __name__ == "__main__":
    ARQUIVO_TXT = "anotacoes.txt"
    
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