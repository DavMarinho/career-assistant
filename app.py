import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Mentora de Carreira AI",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
        "error_generic": "⚠️ Erro ao conectar. Tente novamente.",
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
        "error_generic": "⚠️ Connection error. Please try again.",
        "footer": "AI Career Mentor · Developed by Davi Marinho",
    },
}

SYSTEM_PROMPT_PT = """Você é uma mentora de carreira experiente, empática e direta.

Ajude pessoas de qualquer área e nível de experiência a conquistarem seus objetivos profissionais.

FOCO PRINCIPAL:
- Orientação de carreira para qualquer área
- Currículo, LinkedIn e carta de apresentação
- Preparação para entrevistas
- Transição de carreira e recolocação
- Negociação de salário e benefícios
- Mercado de trabalho, tendências e melhores empresas por área
- Primeiro emprego, estágios e trainee
- Empreendedorismo e freelance
- Soft skills, hard skills e networking

PERGUNTAS FORA DO ASSUNTO:
Responda brevemente e redirecione: "Essa não é bem minha área 😄 Mas posso te ajudar com sua carreira! Tem alguma dúvida profissional?"

ESTILO:
- Empática, encorajadora e direta
- Linguagem simples e acessível
- Dicas práticas e aplicáveis
- Faça perguntas para entender melhor a situação
- Responda SEMPRE em português brasileiro"""

SYSTEM_PROMPT_EN = """You are an experienced, empathetic and direct career mentor.

Help people from any field and experience level achieve their professional goals.

MAIN FOCUS:
- Career guidance for any field
- Resume, LinkedIn and cover letter
- Interview preparation
- Career transitions and job replacement
- Salary and benefits negotiation
- Job market, trends and best companies by field
- First jobs, internships and trainee programs
- Entrepreneurship and freelancing
- Soft skills, hard skills and networking

OFF-TOPIC QUESTIONS:
Respond briefly and redirect: "That's not quite my area 😄 But I can help with your career! Any professional questions?"

STYLE:
- Empathetic, encouraging and direct
- Simple, accessible language
- Practical, immediately applicable tips
- Ask questions to understand the situation better
- ALWAYS respond in English"""


def get_api_key() -> str:
    # 1. tenta pegar do Streamlit Secrets (produção)
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            return key
    except Exception:
        pass
    # 2. fallback: sessão do usuário (desenvolvimento local)
    return st.session_state.get("api_key", "")


def has_server_key() -> bool:
    try:
        return bool(st.secrets["GEMINI_API_KEY"])
    except Exception:
        return False


def get_gemini_response(api_key: str, history: list, lang: str) -> str:
    genai.configure(api_key=api_key)
    system = SYSTEM_PROMPT_PT if lang == "PT" else SYSTEM_PROMPT_EN
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system,
    )
    gemini_history = []
    for msg in history[:-1]:
        gemini_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [msg["content"]],
        })
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(history[-1]["content"])
    return response.text.strip()


st.markdown("""
<style>
.mentor-avatar {
    width:40px;height:40px;border-radius:50%;
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    display:flex;align-items:center;justify-content:center;
    font-size:18px;flex-shrink:0;
}
.msg-mentor {
    background:var(--secondary-background-color);
    border-radius:0 16px 16px 16px;
    padding:12px 16px;margin:4px 0;
    max-width:85%;font-size:15px;line-height:1.6;
}
.msg-user {
    background:#667eea;color:white;
    border-radius:16px 0 16px 16px;
    padding:12px 16px;margin:4px 0;
    max-width:85%;font-size:15px;line-height:1.6;
    margin-left:auto;
}
.msg-row{display:flex;gap:10px;margin:8px 0;align-items:flex-start;}
.msg-row-user{display:flex;justify-content:flex-end;margin:8px 0;}
</style>
""", unsafe_allow_html=True)


def main():
    col_lang = st.columns([6, 1])
    with col_lang[1]:
        lang = st.selectbox("🌐", ["PT", "EN"], label_visibility="collapsed")

    t = TEXTS["pt"] if lang == "PT" else TEXTS["en"]

    st.markdown(f"## {t['title']}")
    st.markdown(f"<p style='color:#888;margin-top:-12px;margin-bottom:20px'>{t['subtitle']}</p>", unsafe_allow_html=True)

    # só mostra campo de API key se não tiver chave no servidor
    if not has_server_key():
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

    # inicializa histórico
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["lang"] = lang

    if st.session_state.get("lang") != lang:
        st.session_state["messages"] = []
        st.session_state["lang"] = lang

    # boas-vindas
    if not st.session_state["messages"]:
        st.markdown(f"""
        <div class="msg-row">
            <div class="mentor-avatar">🎯</div>
            <div class="msg-mentor">{t['welcome'].replace(chr(10), '<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

    # histórico
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
                <div class="mentor-avatar">🎯</div>
                <div class="msg-mentor">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    # input
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

    # envio
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

    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center;color:#aaa;font-size:12px'>{t['footer']}</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()