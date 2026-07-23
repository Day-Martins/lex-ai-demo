<div align="center">
  <img src="assets/logo_lex.png" alt="Logotipo da LEX AI em fundo preto" width="420">

  # LEX AI

  **Plataforma de Inteligência Jurídica Especializada**

  Inteligências artificiais organizadas por área do Direito, com foco em precisão, fontes verificáveis, segurança e controle de escopo.
</div>

> **Status do projeto:** MVP funcional em evolução, com controle de acesso,
> administração de usuários, integração com a Fiscus AI e monitoramento de
> atualizações jurídicas.

## Sobre o projeto

A LEX AI foi concebida para reunir ambientes de inteligência artificial especializados em diferentes ramos do Direito. Cada especialidade poderá contar com regras, fontes, base de conhecimento e limites próprios, oferecendo uma experiência mais organizada e adequada ao contexto jurídico.

O projeto utiliza uma identidade visual institucional em preto, azul-noturno e dourado e apresenta uma interface responsiva construída com Streamlit.

## Funcionalidades

### Disponíveis no MVP

- página inicial institucional;
- acesso e solicitação de cadastro com aprovação administrativa;
- senhas protegidas por hash `scrypt`;
- área de conta para atualização de perfil e troca de senha;
- bloqueio, reativação e redefinição de senha por link temporário;
- apresentação da especialidade Direito Tributário — Fiscus AI;
- painel de atualizações jurídicas alimentado por fontes oficiais;
- indicação visual de módulos disponíveis e em desenvolvimento;
- componentes reutilizáveis de cabeçalho, rodapé e cards;
- layout responsivo e identidade visual própria.

### Próximas etapas

- ambientes de IA separados por especialidade jurídica;
- especialidades Trabalhista e Empresarial;
- integração de autenticação única entre a LEX AI e cada especialidade;
- ampliação das fontes de monitoramento legislativo e regulatório.

## Tecnologias

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)

## Estrutura do projeto

```text
LEX AI/
├── README.md
├── Documentação/
├── Imagens/
└── lex-ai-demo/
    ├── app/
    │   ├── Página_Inicial.py
    │   ├── pages/
    │   └── utils/
    ├── assets/
    ├── database/
    ├── services/
    └── requirements.txt
```

## Como executar localmente

### Pré-requisitos

- Python 3.10 ou superior;
- `pip` disponível no terminal;
- Git, caso queira clonar o repositório.

### Instalação

1. Clone o repositório e acesse a pasta do projeto:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd "LEX AI/lex-ai-demo"
   ```

2. Crie e ative um ambiente virtual:

   **macOS ou Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows (PowerShell)**

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Inicie a aplicação:

   ```bash
   streamlit run "app/Página_Inicial.py"
   ```

5. Acesse o endereço exibido no terminal, normalmente:

   ```text
   http://localhost:8501
   ```

## Configuração

Credenciais e dados sensíveis devem ser configurados por variáveis de ambiente
ou em um arquivo `.env` local não versionado, nunca diretamente no código-fonte.
Copie `.env.example` apenas como referência dos nomes necessários.

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/lex_ai
LEX_ADMIN_USERNAME=dmt
LEX_ADMIN_EMAIL=administrador@exemplo.com
LEX_ADMIN_INITIAL_PASSWORD=uma-senha-inicial-forte
LEX_PUBLIC_URL=https://lex.54-94-43-149.sslip.io
SMTP_HOST=smtp.exemplo.com
SMTP_PORT=587
SMTP_USERNAME=usuario
SMTP_PASSWORD=senha
SMTP_FROM=LEX AI <nao-responda@exemplo.com>
```

O administrador `dmt` é criado somente quando ainda não existe e quando a
variável `LEX_ADMIN_INITIAL_PASSWORD` foi definida. Em bases existentes, a
inicialização nunca troca sua senha.

Sem `DATABASE_URL`, a aplicação usa um banco SQLite local em `data/lex_ai.db`.
Em produção, use PostgreSQL e configure o servidor SMTP para que os usuários
recebam a aprovação e os links de redefinição.

Não versione arquivos `.env`, chaves de API, senhas, bancos locais ou o
diretório `.venv`.

## Identidade visual

| Elemento | Cor |
|---|---|
| Preto Jurídico | `#0B0F14` |
| Azul Noturno | `#111827` |
| Dourado Institucional | `#C9A227` |
| Dourado Claro | `#D8B45A` |
| Branco Gelo | `#F5F7FA` |
| Cinza Jurídico | `#9CA3AF` |

## Aviso importante

A LEX AI é uma ferramenta de apoio à pesquisa e à análise jurídica. As informações apresentadas não substituem a avaliação técnica de profissionais habilitados nem constituem parecer jurídico.

## Contribuição

O projeto está em fase inicial. Para contribuir, crie uma branch específica, faça alterações de escopo reduzido e abra um pull request descrevendo o objetivo e os testes realizados.

## Autoria

Desenvolvido por **DMT Data Consulting**.
