import json
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

MAX_PROMPT_CHARS = 12000

CLAUDE_MODELS = [
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-6",
    "claude-haiku-4-5-20251001",
    "claude-3-haiku-20240307",
]

ANALYSIS_PROMPT_TEMPLATE = """Você é um analista de negócios especializado em identificar oportunidades de automação com IA em empresas.

CONTEXTO: Este grupo discute PROBLEMAS REAIS DO NEGÓCIO e como usar IA para resolvê-los.
Os dados abaixo incluem mensagens de texto E transcrições de vídeos/reels compartilhados no grupo.
Analise AMBOS com o mesmo peso — os vídeos frequentemente contêm relatos detalhados de problemas e soluções.

═══════════════════════════════════════════════════════════════════

🎯 SUA MISSÃO: Extrair insights para DECISÕES ESTRATÉGICAS sobre onde investir em IA

═══════════════════════════════════════════════════════════════════

📊 CATEGORIA 1: PROBLEMAS_OPERACIONAIS (Dores do Negócio/Empresa)

   O QUE PROCURAR:
   ✓ Problemas do dia-a-dia da operação/negócio
   ✓ Processos manuais demorados
   ✓ Gargalos, ineficiências, retrabalho
   ✓ Custos altos, desperdício de tempo
   ✓ Erros humanos recorrentes
   ✓ Dificuldades de escala

   FORMATO DE SAÍDA:
   {{
     "problema": "descrição do problema específico",
     "area": "departamento/área afetada (ex: Atendimento, Vendas, RH, Financeiro)",
     "frequencia": "diária/semanal/mensal ou número de vezes mencionado",
     "impacto": "alto/médio/baixo (baseado em palavras como 'crítico', 'urgente', 'perco tempo')"
   }}

   EXEMPLOS:
   ❌ ERRADO: {{"problema": "ChatGPT está lento"}}
   ✅ CORRETO: {{"problema": "Atendimento demora 2h para responder cada cliente", "area": "Atendimento", "frequencia": "diária", "impacto": "alto"}}

═══════════════════════════════════════════════════════════════════

🤖 CATEGORIA 2: SOLUCOES_IA_IMPLEMENTADAS (O que já está sendo feito)

   O QUE PROCURAR:
   ✓ Relatos de uso de IA (ChatGPT, Claude, Gemini, etc.)
   ✓ Automações já criadas
   ✓ Resultados obtidos (tempo economizado, erros reduzidos)

   FORMATO DE SAÍDA:
   {{
     "solucao": "o que foi feito com IA",
     "problema_resolvido": "qual problema foi resolvido",
     "resultado": "resultado obtido (tempo economizado, etc.)",
     "ferramenta": "ChatGPT/Claude/Make/n8n/etc"
   }}

   EXEMPLO:
   {{"solucao": "Usei ChatGPT para gerar respostas padrão", "problema_resolvido": "Demora para responder clientes", "resultado": "Reduziu tempo de 2h para 15min", "ferramenta": "ChatGPT"}}

═══════════════════════════════════════════════════════════════════

💡 CATEGORIA 3: OPORTUNIDADES_IA (Onde PODE usar IA mas ainda NÃO usa)

   O QUE PROCURAR:
   ✓ Ideias de automação mencionadas
   ✓ "Dá pra usar IA pra...", "Precisamos automatizar..."
   ✓ Problemas sem solução atual

   FORMATO DE SAÍDA:
   {{
     "oportunidade": "descrição da oportunidade",
     "problema_alvo": "qual problema resolveria",
     "viabilidade": "alta/média/baixa (baseado em complexidade mencionada)"
   }}

═══════════════════════════════════════════════════════════════════

🔗 CATEGORIA 4: LINKS_FERRAMENTAS

   Copie URLs exatas de ferramentas, tutoriais, documentação mencionados

═══════════════════════════════════════════════════════════════════

🏢 CATEGORIA 5: AREAS_IMPACTADAS

   Liste departamentos/áreas mencionados: ["Vendas", "Atendimento", "RH", "Marketing", ...]

═══════════════════════════════════════════════════════════════════

⚠️ REGRAS CRÍTICAS:

1. PROBLEMAS DE NEGÓCIO ≠ PROBLEMAS COM IA
   - "ChatGPT caiu" → NÃO é problema operacional
   - "Levo 3h por dia copiando dados manualmente" → SIM é problema operacional

2. SEJA ULTRA-ESPECÍFICO
   - Inclua números, nomes, detalhes
   - Use palavras EXATAS dos participantes

3. CLASSIFIQUE IMPACTO/URGÊNCIA
   - Palavras-chave ALTO: "urgente", "crítico", "perco muito tempo", "todo dia"
   - Palavras-chave MÉDIO: "seria bom", "às vezes", "ajudaria"
   - Palavras-chave BAIXO: "talvez", "um dia", "interessante"

4. IGNORE SPAM/SAUDAÇÕES

═══════════════════════════════════════════════════════════════════

MENSAGENS:

{messages}

═══════════════════════════════════════════════════════════════════

RESPONDA APENAS COM JSON VÁLIDO (sem comentários, sem ```):

{{
  "problemas_operacionais": [
    {{"problema": "...", "area": "...", "frequencia": "...", "impacto": "..."}},
    ...
  ],
  "solucoes_ia_implementadas": [
    {{"solucao": "...", "problema_resolvido": "...", "resultado": "...", "ferramenta": "..."}},
    ...
  ],
  "oportunidades_ia": [
    {{"oportunidade": "...", "problema_alvo": "...", "viabilidade": "..."}},
    ...
  ],
  "links_ferramentas": ["url1", "url2", ...],
  "areas_impactadas": ["area1", "area2", ...]
}}

LEMBRE-SE: Foque em PROBLEMAS DE NEGÓCIO, não problemas técnicos com IA."""


def analyze_with_claude(messages, api_key, model, status_placeholder, prepared_text=None):
    client = Anthropic(api_key=api_key)

    if prepared_text:
        truncated_input = prepared_text[:MAX_PROMPT_CHARS]
        if len(prepared_text) > MAX_PROMPT_CHARS:
            chars_removed = len(prepared_text) - MAX_PROMPT_CHARS
            status_placeholder.warning(
                f"⚠️ Conteúdo muito longo! Analisando apenas os primeiros {MAX_PROMPT_CHARS} "
                f"caracteres ({chars_removed} caracteres ignorados)."
            )
    else:
        text_blob = "\n".join([f"- {m['text']}" for m in messages])
        truncated_input = text_blob[:MAX_PROMPT_CHARS]
        if len(text_blob) > MAX_PROMPT_CHARS:
            chars_removed = len(text_blob) - MAX_PROMPT_CHARS
            status_placeholder.warning(
                f"⚠️ Mensagens muito longas! Analisando apenas os primeiros {MAX_PROMPT_CHARS} "
                f"caracteres ({chars_removed} caracteres ignorados)."
            )

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(messages=truncated_input)

    models_to_try = [model] + [m for m in CLAUDE_MODELS if m != model]

    last_error = None
    for try_model in models_to_try:
        status_placeholder.markdown(f"🔄 Tentando analisar com **{try_model}**...")

        try:
            response = client.messages.create(
                model=try_model,
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text.strip()
            json_str = response_text
            if json_str.startswith("```json"):
                json_str = json_str[7:-3]
            elif json_str.startswith("```"):
                json_str = json_str[3:-3]

            result = json.loads(json_str)
            result["_model_used"] = try_model
            result["_raw_response"] = response_text
            status_placeholder.success(f"✅ Sucesso com modelo: **{try_model}**")
            return result

        except Exception as e:
            error_str = str(e)
            last_error = error_str
            logger.warning("Erro com modelo %s: %s", try_model, error_str)

            if "404" in error_str or "not_found" in error_str.lower():
                continue
            elif "429" in error_str or "rate_limit" in error_str.lower():
                return {
                    "error": f"Limite de taxa excedido. Aguarde alguns minutos e tente novamente. Erro: {error_str}"
                }
            elif "authentication" in error_str.lower() or "api_key" in error_str.lower():
                return {
                    "error": f"Erro de autenticação. Verifique sua API Key. Erro: {error_str}"
                }

    return {
        "error": f"Nenhum modelo disponível funcionou. Último erro: {last_error}. "
        "Verifique sua API Key em console.anthropic.com e confirme quais modelos você tem acesso."
    }
