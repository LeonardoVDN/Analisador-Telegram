# Analisador de Grupos Telegram MVP 🕵️‍♂️

Um MVP para extrair mensagens de grupos do Telegram e processar com IA (Anthropic Claude) para gerar insights sobre Dores, Ideias e Temas.

## Pré-requisitos

1. **Python 3.9+** instalado
2. **Anthropic Claude API Key** (gratuita)

## 🔑 Como obter as Credenciais

### 1. Telegram (API ID e API Hash)
O Telegram exige que você registre um "aplicativo" para acessar a API deles.
1.  Acesse **[my.telegram.org](https://my.telegram.org/auth)**.
2.  Digite seu número de telefone (formato internacional, ex: `+5511999999999`) e clique em **Next**.
3.  O Telegram enviará um código de confirmação para o seu **app do Telegram** (não por SMS).
4.  Digite o código no site e faça login.
5.  Clique em **API development tools**.
6.  Preencha o formulário:
    *   **App title**: Escolha um nome (ex: `MeuAnalisador`).
    *   **Short name**: Escolha um nome curto (ex: `meuanalisador`).
    *   **Platform**: Pode deixar `Desktop`.
    *   **URL**: Pode deixar em branco ou colocar `http://localhost`.
7.  Clique em **Create application**.
8.  **Copie o `App api_id` e o `App api_hash`**. Você precisará deles no dashboard.

### 2. Anthropic Claude (API Key)
A API do Claude é gratuita para uso inicial com créditos promocionais.

1. Acesse **[Anthropic Console](https://console.anthropic.com/settings/keys)**
2. Faça login ou crie uma conta
3. Clique em **"Create Key"**
4. Dê um nome para a chave (ex: "Telegram Analyzer")
5. **Copie a chave gerada** (começa com `sk-ant-...`)

## Instalação

```bash
pip install -r requirements.txt
```

## Como Rodar

```bash
streamlit run app.py
```

## Funcionalidades

* **Login Seguro**: Suporte a 2FA e código de verificação do Telegram
* **Extração Flexível**: Funciona com Links (`https://t.me/grupo`) ou Usernames (`@grupo`)
* **IA Avançada**: Usa Anthropic Claude para análise precisa e detalhada
* **Dashboard Visual**: Exibe métricas e cards com os insights gerados
* **3 Modelos Disponíveis**: Sonnet (recomendado), Haiku (rápido), Opus (máxima qualidade)
* **Modo Debug**: Visualize a resposta bruta do modelo para verificar a qualidade

## Vantagens do Anthropic Claude

✅ **Qualidade Superior** - Um dos melhores modelos de IA do mundo
✅ **Confiável** - Sem problemas de quota como outros provedores
✅ **Rápido** - Respostas em poucos segundos
✅ **Excelente em Português** - Treinado em múltiplos idiomas
✅ **Free Tier Generoso** - Créditos iniciais gratuitos

## Notas

* Os dados da sessão do Telegram são salvos localmente em arquivos `.session`
* A API do Claude oferece créditos gratuitos iniciais
* Configure a API Key do Claude na sidebar antes de analisar
* Claude 3.5 Sonnet é recomendado para melhor equilíbrio qualidade/velocidade
