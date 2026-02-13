# Analisador de Grupos Telegram MVP 🕵️‍♂️

Um MVP para extrair mensagens de grupos do Telegram, processar vídeos/reels compartilhados e analisar tudo com IA (Anthropic Claude) para gerar insights estratégicos sobre problemas operacionais e oportunidades de automação com IA.

## Pré-requisitos

1. **Python 3.9+** instalado
2. **Anthropic Claude API Key**
3. **ffmpeg** instalado no sistema (`brew install ffmpeg` no macOS)

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

1. Acesse **[Anthropic Console](https://console.anthropic.com/settings/keys)**
2. Faça login ou crie uma conta
3. Clique em **"Create Key"**
4. Dê um nome para a chave (ex: "Telegram Analyzer")
5. **Copie a chave gerada** (começa com `sk-ant-...`)

## Instalação

```bash
pip install -r requirements.txt
brew install ffmpeg
```

O modelo de transcrição (`faster-whisper base`) será baixado automaticamente na primeira execução (~150MB).

## Como Rodar

```bash
streamlit run app.py
```

## Fluxo de Uso

O app funciona em 3 etapas:

1. **📥 Baixar Mensagens** — Conecta ao Telegram, baixa mensagens de texto e vídeos do grupo
2. **🎙️ Processar Mídias** *(opcional)* — Baixa vídeos de links (Reels, YouTube, TikTok), extrai áudio e transcreve localmente com IA
3. **🤖 Analisar com IA** — Envia mensagens + transcrições para o Claude, que retorna análise estruturada
4. **📄 Exportar Relatório** — Gera um HTML estático para compartilhar com a equipe

## Funcionalidades

* **Login Seguro**: Suporte a 2FA e código de verificação do Telegram
* **Extração Flexível**: Funciona com Links (`https://t.me/grupo`) ou Usernames (`@grupo`)
* **Processamento de Vídeos**: Baixa e transcreve vídeos do chat e links externos (Instagram Reels, YouTube, TikTok, X/Twitter)
* **Transcrição Local**: Usa `faster-whisper` para transcrever áudio localmente, sem enviar dados para serviços externos
* **Resiliência**: Se um vídeo falhar no download ou transcrição, o fluxo continua com os demais
* **IA Avançada**: Usa Anthropic Claude para análise de problemas operacionais e oportunidades de IA
* **Dashboard Visual**: Exibe métricas, problemas priorizados, oportunidades e recomendações
* **Exportar Relatório HTML**: Gera um relatório estático para compartilhar online com a equipe (sem expor credenciais)
* **4 Modelos Disponíveis**: Sonnet 4.5 (recomendado), Opus 4.6 (máxima qualidade), Haiku 4.5 (rápido), Haiku 3 (legacy)

## Estrutura do Projeto

```
├── app.py                 # Interface principal (Streamlit)
├── telegram_ops.py        # Operações com a API do Telegram
├── media_processing.py    # Download, extração de áudio e transcrição de vídeos
├── data_preparation.py    # Preparação e organização dos dados para a IA
├── claude_analysis.py     # Análise com Anthropic Claude
├── dashboard.py           # Renderização do dashboard de resultados
├── report_export.py       # Geração do relatório HTML exportável
├── helpers.py             # Funções utilitárias e validações
└── requirements.txt       # Dependências do projeto
```

## Compartilhando o Relatório

Após exportar o HTML, você pode colocá-lo online gratuitamente:

* **Netlify Drop** — Arraste o arquivo em [app.netlify.com/drop](https://app.netlify.com/drop) e receba um link público
* **Tiiny.host** — Upload direto de HTML
* **GitHub Pages** — Hospede no seu repositório

## Notas

* Os dados da sessão do Telegram são salvos localmente em arquivos `.session`
* A transcrição de vídeos roda 100% local (sem envio de áudio para APIs externas)
* Vídeos maiores que 100MB são ignorados automaticamente
* O limite de contexto para a IA é de 12.000 caracteres (mensagens de texto têm prioridade de 60%, transcrições 40%)
