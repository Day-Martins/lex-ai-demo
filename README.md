<div align="center">
  <img src="assets/lex_neutro.png" alt="Logotipo da LEX AI" width="150">

  # LEX AI

  **Plataforma de Inteligência Jurídica Especializada**

  Inteligências artificiais organizadas por área do Direito, com foco em precisão, fontes verificáveis, segurança e controle de escopo.
</div>

> **Status do projeto:** MVP em desenvolvimento. Atualmente, o repositório disponibiliza a interface institucional e a navegação inicial da plataforma.

## Sobre o projeto

A LEX AI foi concebida para reunir ambientes de inteligência artificial especializados em diferentes ramos do Direito. Cada especialidade poderá contar com regras, fontes, base de conhecimento e limites próprios, oferecendo uma experiência mais organizada e adequada ao contexto jurídico.

O projeto utiliza uma identidade visual institucional em preto, azul-noturno e dourado e apresenta uma interface responsiva construída com Streamlit.

## Funcionalidades

### Disponíveis no MVP

- página inicial institucional;
- apresentação das especialidades jurídicas;
- indicação visual de módulos disponíveis e em desenvolvimento;
- seção de monitoramento jurídico;
- componentes reutilizáveis de cabeçalho, rodapé e cards;
- layout responsivo e identidade visual própria.

### Em desenvolvimento

- ambientes de IA separados por especialidade jurídica;
- módulo de Reforma Tributária — **LEX Tributário**;
- especialidades Trabalhista e Empresarial;
- acompanhamento de atualizações legislativas e regulatórias;
- autenticação e controle de acesso;
- área do usuário e painel administrativo;
- persistência de dados em PostgreSQL.

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

## Configuração futura

Os módulos de integração ainda estão em desenvolvimento. Quando forem habilitados, credenciais e dados sensíveis deverão ser configurados por variáveis de ambiente ou por `st.secrets`, nunca diretamente no código-fonte. Exemplos previstos:

```env
OPENAI_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/lex_ai
```

Não versione arquivos `.env`, chaves de API, senhas, bancos locais ou o diretório `.venv`.

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
