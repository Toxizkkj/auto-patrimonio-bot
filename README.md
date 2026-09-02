# Projeto Consolidado: Este bot foi integrado à Central de Automações RPA. O desenvolvimento ativo continua por lá.

#  Asset Management System — Controle de Patrimônio e Equipamentos de TI

Aplicação para rastreamento, inventário e controle de ciclo de vida de ativos de hardware e infraestrutura de TI.

##  Problema de Negócio
A falta de centralização no controle de periféricos, componentes e máquinas alocadas em setores corporativos gerava divergências de inventário, perda de histórico de manutenção e dificuldade em auditorias de equipamentos.

##  Solução
Sistema estruturado para cadastro, categorização e rastreio de status de ativos de TI (computadores, periféricos, peças e suprimentos), permitindo vincular responsáveis, setores e histórico de movimentações.

##  Tecnologias & Arquitetura
* **Backend / Lógica**: Python / Banco de Dados Relacional (SQLite / PostgreSQL)
* **Modelagem de Dados**: Entidades de Ativos, Categorias, Movimentações e Usuários
* **Camada de Interface/API**: Interface modular para CRUD e relatórios de auditoria

##  Funcionalidades Principais
* **Cadastro de Ativos**: Registro detalhado por número de série, etiqueta de patrimônio, especificações e estado de conservação.
* **Histórico de Movimentação**: Rastreabilidade de transferências entre colaboradores e setores.
* **Controle de Status**: Monitoramento de itens em uso, manutenção, reserva ou descarte.
* **Busca e Filtros Rápidos**: Consulta por setor, etiqueta de patrimônio ou responsável.

##  Como Executar

1. **Clonar e instalar dependências**:
   ```bash
   git clone [https://github.com/SEU_USUARIO/nome-do-repo-patrimonio.git](https://github.com/SEU_USUARIO/nome-do-repo-patrimonio.git)
   cd nome-do-repo-patrimonio
   pip install -r requirements.txt
