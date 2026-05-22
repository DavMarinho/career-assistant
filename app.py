import streamlit as st
import google.generativeai as genai
import re

# ── Página ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Carla – Mentora de Carreira",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Textos ─────────────────────────────────────────────────────────
TEXTS = {
    "pt": {
        "title": "🎯 Mentora de Carreira AI",
        "subtitle": "Sua assistente de carreira com Inteligência Artificial",
        "api_label": "Chave da API Gemini",
        "api_help": "Obtenha grátis em aistudio.google.com",
        "api_placeholder": "AIza...",
        "placeholder": "Digite sua mensagem...",
        "send": "Enviar",
        "clear": "🗑️ Limpar conversa",
        "thinking": "Pensando...",
        "welcome": "Olá! Sou sua mentora de carreira com IA 👋\n\nEstou aqui para te ajudar com:\n- 📄 Currículo e LinkedIn\n- 🎯 Escolha de carreira\n- 💼 Preparação para entrevistas\n- 📈 Crescimento profissional\n- 🔄 Transição de área\n- 💰 Negociação de salário\n\nComo posso te ajudar hoje?",
        "error_api": "⚠️ Chave de API inválida ou sem créditos.",
        "error_generic": "⚠️ Erro ao conectar. Verifique sua chave e tente novamente.",
        "api_saved": "✓ API Key salva",
        "footer": "Mentora de Carreira AI · Desenvolvido por Davi Marinho",
    },
    "en": {
        "title": "🎯 AI Career Mentor",
        "subtitle": "Your AI-powered Career Assistant",
        "api_label": "Gemini API Key",
        "api_help": "Get it free at aistudio.google.com",
        "api_placeholder": "AIza...",
        "placeholder": "Type your message...",
        "send": "Send",
        "clear": "🗑️ Clear conversation",
        "thinking": "Thinking...",
        "welcome": "Hi! I'm your AI career mentor 👋\n\nI'm here to help you with:\n- 📄 Resume and LinkedIn\n- 🎯 Career choice\n- 💼 Interview preparation\n- 📈 Professional growth\n- 🔄 Career transition\n- 💰 Salary negotiation\n\nHow can I help you today?",
        "error_api": "⚠️ Invalid API key or no credits.",
        "error_generic": "⚠️ Connection error. Check your key and try again.",
        "api_saved": "✓ API Key saved",
        "footer": "AI Career Mentor · Developed by Davi Marinho",
    },
}

# ── Persona da Carla ───────────────────────────────────────────────
SYSTEM_PROMPT_PT = """Você é uma mentora de carreira experiente, empática e direta chamada Carla.

Seu objetivo é ajudar pessoas de qualquer área e nível de experiência a conquistarem seus objetivos profissionais.

FOCO PRINCIPAL — você responde com profundidade sobre:
- Orientação de carreira para qualquer área profissional
- Currículo, carta de apresentação e perfil no LinkedIn
- Preparação para entrevistas de emprego
- Transição de carreira e recolocação
- Desenvolvimento profissional e habilidades
- Negociação de salário e benefícios
- Mercado de trabalho, tendências e melhores empresas por área
- Primeiro emprego, estágios e trainee
- Empreendedorismo e trabalho freelance
- Soft skills e hard skills
- Networking e construção de marca pessoal

PERGUNTAS FORA DO ASSUNTO:
Se alguém perguntar algo que não tem relação com carreira ou trabalho (ex: previsão do tempo, receitas, esportes, política), responda de forma simpática e breve, e redirecione para o foco:
Exemplo: "Essa não é bem minha área de especialidade 😄 Mas se quiser, posso te ajudar com sua carreira! Tem alguma dúvida profissional que posso resolver?"

Seu estilo:
- Seja empática, encorajadora e direta
- Use linguagem simples e acessível
- Dê dicas práticas e aplicáveis imediatamente
- Faça perguntas para entender melhor a situação da pessoa
- Celebre as conquistas do usuário
- Seja honesta quando algo for difícil, mas sempre motivadora
- Use exemplos reais quando possível
- Responda SEMPRE em português brasileiro

Lembre-se: você está falando com pessoas que podem estar inseguras, em transição ou sem experiência. Seja acolhedora e confiante."""

SYSTEM_PROMPT_EN = """You are an experienced, empathetic and direct career mentor named Carla.

Your goal is to help people from any field and experience level achieve their professional goals.

MAIN FOCUS — you answer in depth about:
- Career guidance for any professional field
- Resume, cover letter and LinkedIn profile
- Job interview preparation
- Career transitions and job replacement
- Professional development and skills
- Salary and benefits negotiation
- Job market, trends and best companies by field
- First jobs, internships and trainee programs
- Entrepreneurship and freelancing
- Soft skills and hard skills
- Networking and personal branding

OFF-TOPIC QUESTIONS:
If someone asks something unrelated to career or work (e.g. weather forecast, recipes, sports, politics), respond briefly and kindly, then redirect:
Example: "That's not quite my area of expertise 😄 But I'd love to help with your career! Do you have any professional questions I can help with?"

Your style:
- Be empathetic, encouraging and direct
- Use simple, accessible language
- Give practical, immediately applicable tips
- Ask questions to better understand the person's situation
- Celebrate user achievements
- Be honest when something is difficult, but always motivating
- Use real examples when possible
- ALWAYS respond in English

Remember: you are talking to people who may be insecure, in transition, or without experience. Be welcoming and confident."""

# ── Gemini ─────────────────────────────────────────────────────────
def get_api_key() -> str:
    """Retorna a API key — do servidor (secrets) ou da sessão do usuário."""
    # tenta pegar dos secrets do Streamlit Cloud primeiro
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # fallback para a sessão do usuário
    return st.session_state.get("api_key", "")
    genai.configure(api_key=api_key)
    system = SYSTEM_PROMPT_PT if lang == "PT" else SYSTEM_PROMPT_EN
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system,
    )
    # converte histórico para formato Gemini
    gemini_history = []
    for msg in history[:-1]:  # tudo exceto a última mensagem
        gemini_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [msg["content"]],
        })
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(history[-1]["content"])
    return response.text.strip()

# ── CSS customizado ────────────────────────────────────────────────
st.markdown("""
<style>
/* Avatar da Carla */
.carla-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
/* Bolha de mensagem */
.msg-carla {
    background: var(--secondary-background-color);
    border-radius: 0 16px 16px 16px;
    padding: 12px 16px; margin: 4px 0;
    max-width: 85%; font-size: 15px; line-height: 1.6;
}
.msg-user {
    background: #667eea;
    color: white;
    border-radius: 16px 0 16px 16px;
    padding: 12px 16px; margin: 4px 0;
    max-width: 85%; font-size: 15px; line-height: 1.6;
    margin-left: auto;
}
.msg-row { display: flex; gap: 10px; margin: 8px 0; align-items: flex-start; }
.msg-row-user { display: flex; justify-content: flex-end; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── UI principal ───────────────────────────────────────────────────
def main():
    # idioma
    col_lang = st.columns([6, 1])
    with col_lang[1]:
        lang = st.selectbox("🌐", ["PT", "EN"], label_visibility="collapsed")

    t = TEXTS["pt"] if lang == "PT" else TEXTS["en"]

    st.markdown(f"## {t['title']}")
    st.markdown(f"<p style='color:#888;margin-top:-12px;margin-bottom:20px'>{t['subtitle']}</p>", unsafe_allow_html=True)

    # ── API Key ────────────────────────────────────────────────────
    # verifica se tem chave no servidor
    server_key = False
    try:
        if st.secrets.get("GEMINI_API_KEY"):
            server_key = True
    except Exception:
        pass

    if not server_key:
        saved_key = st.session_state.get("api_key", "")
        with st.expander("🔑 API Key", expanded=not saved_key):
            api_key_input = st.text_input(
                t["api_label"],
                type="password",
                placeholder=t["api_placeholder"],
                help=f"{t['api_help']} → aistudio.google.com",
                value=saved_key,
            )
            if api_key_input:
                st.session_state["api_key"] = api_key_input
                st.caption(t["api_saved"])

    # ── Inicializa histórico ───────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["lang"] = lang

    # reset se mudou idioma
    if st.session_state.get("lang") != lang:
        st.session_state["messages"] = []
        st.session_state["lang"] = lang

    # ── Mensagem de boas-vindas ────────────────────────────────────
    if not st.session_state["messages"]:
        st.markdown(f"""
        <div class="msg-row">
            <div class="carla-avatar">🎯</div>
            <div class="msg-carla">{t['welcome'].replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Histórico de mensagens ─────────────────────────────────────
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row-user">
                <div class="msg-user">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            content = msg['content'].replace('\n', '<br>')
            st.markdown(f"""
            <div class="msg-row">
                <div class="carla-avatar">🎯</div>
                <div class="msg-carla">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Input ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "msg",
            placeholder=t["placeholder"],
            label_visibility="collapsed",
            key="user_input",
        )
    with col_btn:
        send = st.button(t["send"], use_container_width=True, type="primary")

    col_clear, _ = st.columns([2, 5])
    with col_clear:
        if st.button(t["clear"], use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    # ── Envio ──────────────────────────────────────────────────────
    if (send or user_input) and user_input.strip():
        api_key = get_api_key()
        if not api_key:
            st.error(t["error_api"])
            st.stop()

        st.session_state["messages"].append({
            "role": "user",
            "content": user_input.strip(),
        })

        with st.spinner(t["thinking"]):
            try:
                response = get_gemini_response(
                    api_key,
                    st.session_state["messages"],
                    lang,
                )
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": response,
                })
            except Exception as e:
                err = str(e).lower()
                if "api_key" in err or "invalid" in err or "401" in err:
                    st.error(t["error_api"])
                else:
                    st.error(t["error_generic"])
                st.stop()

        st.rerun()

    # ── Footer ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center;color:#aaa;font-size:12px'>{t['footer']}</p>",
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()