# Skill Alexa com OpenAI

Skill Alexa em Python para responder perguntas em portugues do Brasil usando a API da OpenAI.

## Como usar

1. Crie uma conta e uma chave de API na OpenAI:
   https://platform.openai.com/account/api-keys

2. Configure billing/creditos da API:
   https://platform.openai.com/account/billing/overview

   A API da OpenAI e o ChatGPT Plus sao produtos diferentes. A assinatura do ChatGPT Plus nao libera uso da API.

3. Crie uma Skill Alexa-hosted em Python:
   https://developer.amazon.com/alexa/console/ask/create-new-skill

   Configuracao sugerida:
   - Primary locale: Portuguese (BR)
   - Experience type: Other > Custom
   - Hosting: Alexa-hosted (Python)
   - Hosting region: US East (N. Virginia), ou a regiao que voce preferir

4. Importe ou envie este projeto para a skill.

5. Em `lambda/lambda_function.py`, substitua o placeholder pela sua chave da OpenAI:

   ```python
   openai_api_key = "SUBSTITUA-POR-SUA-API-KEY-DA-OPENAI"
   ```

   Neste projeto a chave fica no contexto do Amazon Developer/Alexa-hosted. Nao versione o arquivo com a chave real.

6. Se quiser, altere o modelo:

   ```python
   MODEL = "gpt-4o-mini"
   ```

7. Faca build do modelo de interacao e deploy do codigo.

## Como perguntar

Por causa do tipo de slot `AMAZON.SearchQuery`, a pergunta precisa ter uma frase de apoio antes do texto livre. Exemplos:

- "pergunte quem e o presidente do Brasil"
- "explique o que e computacao quantica"
- "me diga uma receita simples de bolo"
- "minha pergunta e quanto tempo leva para chegar em Marte"

## Limites de uso

O codigo possui limites simples para reduzir risco de custo e conversas longas:

- ate 8 perguntas por sessao;
- pergunta com ate 600 caracteres;
- resposta com ate 450 tokens;
- historico limitado as ultimas 6 mensagens da sessao;
- timeout de 12 segundos na chamada para a OpenAI.

Esses valores ficam em `lambda/lambda_function.py`:

```python
MAX_QUERY_CHARS = 600
MAX_RESPONSE_TOKENS = 450
MAX_TURNS_PER_SESSION = 8
MAX_HISTORY_MESSAGES = 6
```

Para uso publico, tambem configure limites de gasto/budget na conta da OpenAI.

## Privacidade

A fala transcrita pela Alexa e enviada para a OpenAI para gerar a resposta. Evite usar a skill para informacoes sensiveis.

Se voce publicar a skill para outras pessoas, revise as exigencias da Amazon para politica de privacidade e deixe claro que perguntas dos usuarios sao processadas por um servico externo.

## Manifesto da skill

O arquivo `skill.json` nao contem ARN fixo de Lambda. Em uma skill Alexa-hosted, o endpoint deve ser criado e associado pelo proprio ambiente da Amazon durante o deploy.
