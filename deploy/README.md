# Deploy integrado

Este diretório contém o modelo versionado do gateway de acesso compartilhado
entre a LEX AI e a FISCUS AI.

- `auth` executa o portal institucional e usa a base de usuários da LEX;
- `caddy` valida a sessão antes de encaminhar cada acesso às plataformas;
- o cookie de sessão é assinado, `HttpOnly`, `Secure` e limitado aos subdomínios;
- bloqueio de conta ou troca de senha revoga a sessão nas duas plataformas;
- o microfone é permitido apenas para a própria origem, viabilizando gravação
  de áudio nos chats.

## Preparação

1. Copie `.env.example` para `.env` sem versionar o arquivo resultante.
2. Ajuste os contextos de build da LEX e da FISCUS.
3. Gere `AUTH_SESSION_SECRET` com `openssl rand -hex 32`.
4. Confirme que existe ao menos uma conta aprovada na base da LEX.
5. Valide com `docker compose config --quiet`.
6. Faça backup do banco e dos volumes antes de atualizar a produção.

Credenciais, chaves de API, bancos e documentos de clientes não pertencem ao
repositório.
