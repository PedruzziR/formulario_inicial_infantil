import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests
import re

# ================= LISTAS DE REFERÊNCIA =================
ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

OPCOES_ESCOLARIDADE = [
    "Selecione...",
    "Pré-I",
    "Pré-II",
    "1ª Série do Ensino Fundamental",
    "2ª Série do Ensino Fundamental",
    "3ª Série do Ensino Fundamental",
    "4ª Série do Ensino Fundamental",
    "5ª Série do Ensino Fundamental",
    "6ª Série do Ensino Fundamental",
    "7ª Série do Ensino Fundamental",
    "8ª Série do Ensino Fundamental",
    "9ª Série do Ensino Fundamental",
    "1ª Série do Ensino Médio",
    "2ª Série do Ensino Médio",
    "3ª Série do Ensino Médio",
]

# ================= CONEXÃO COM GOOGLE SHEETS =================
@st.cache_resource
def conectar_planilha():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    client = gspread.authorize(creds)
    # IMPORTANTE: Crie uma aba com este nome exato na sua planilha!
    return client.open("Controle_Tokens").worksheet("Formulario_Infantil")

try:
    planilha_triagem = conectar_planilha()
except Exception as e:
    st.error(f"Erro de conexão com a planilha: {e}")
    st.stop()

# ================= CONFIGURAÇÕES DE E-MAIL =================
SEU_EMAIL = st.secrets["EMAIL_USUARIO"]
SENHA_DO_EMAIL = st.secrets["SENHA_USUARIO"]

def enviar_email_triagem(dados):
    assunto = f"Novo Formulário Inicial Infantil - {dados['Nome do(a) Paciente']}"
    corpo = "Um novo formulário de triagem INFANTIL foi preenchido.\n\n"
    for chave, valor in dados.items():
        corpo += f"{chave}: {valor}\n"

    msg = MIMEMultipart()
    msg['From'] = SEU_EMAIL
    msg['To'] = "psicologabrunaligoski@gmail.com"
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SENHA_DO_EMAIL)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ================= FUNÇÕES DE APOIO =================
def buscar_cep(cep_input):
    cep_limpo = re.sub(r'\D', '', cep_input)
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                dados = r.json()
                if "erro" not in dados:
                    return dados
        except:
            return None
    return None

def aplicar_mascaras():
    # Responsável
    if "cpf_resp_key" in st.session_state and st.session_state.cpf_resp_key:
        nums = re.sub(r'\D', '', st.session_state.cpf_resp_key)
        if len(nums) == 11: st.session_state.cpf_resp_key = f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    if "nasc_resp_key" in st.session_state and st.session_state.nasc_resp_key:
        nums = re.sub(r'\D', '', st.session_state.nasc_resp_key)
        if len(nums) == 8: st.session_state.nasc_resp_key = f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
    if "tel_key" in st.session_state and st.session_state.tel_key:
        nums = re.sub(r'\D', '', st.session_state.tel_key)
        if len(nums) == 11: st.session_state.tel_key = f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
        elif len(nums) == 10: st.session_state.tel_key = f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
        
    # Paciente
    if "cpf_pac_key" in st.session_state and st.session_state.cpf_pac_key:
        nums = re.sub(r'\D', '', st.session_state.cpf_pac_key)
        if len(nums) == 11: st.session_state.cpf_pac_key = f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    if "nasc_pac_key" in st.session_state and st.session_state.nasc_pac_key:
        nums = re.sub(r'\D', '', st.session_state.nasc_pac_key)
        if len(nums) == 8: st.session_state.nasc_pac_key = f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"

# ================= INTERFACE =================
st.set_page_config(page_title="Formulário Inicial Infantil", layout="centered")

st.markdown("""
    <style>
    .stButton > button {
        background-color: #0047AB !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

if "enviado" not in st.session_state:
    st.session_state.enviado = False

st.markdown("<h1 style='text-align: center;'>Clínica de Psicologia e Psicanálise Bruna Ligoski</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>Formulário Inicial - Avaliação Neuropsicológica Infantil</h4>", unsafe_allow_html=True)

if st.session_state.enviado:
    st.success("Formulário enviado com sucesso! Agradecemos o preenchimento.")
    st.stop()

st.divider()

# --- LGPD ---
st.markdown("<h3 style='text-align: center;'>Termo de Consentimento para Tratamento de Dados Pessoais</h3>", unsafe_allow_html=True)
termo_html = """
<div style="border: 1px solid white; border-radius: 10px; padding: 20px; margin-top: 10px; margin-bottom: 20px; text-align: justify;">
Em conformidade com a Lei nº 13.709/2018 – Lei Geral de Proteção de Dados Pessoais (LGPD), autorizo o uso dos meus dados pessoais informados neste formulário para as finalidades específicas de construção do laudo de Avaliação Neuropsicológica e em caso de certificação da atividade do conveniado junto ao seu convênio, se neste caso existir.<br><br>
Meus dados serão armazenados e utilizados de forma segura e sigilosa, exclusivamente pela Clínica de Psicologia e Psicanálise Bruna Ligoski, respeitando a legislação vigente.<br><br>
Estou ciente de que posso solicitar a qualquer momento o acesso, correção ou exclusão dos meus dados por meio do contato de e-mail psicologabrunaligoski@gmail.com.
</div>
"""
st.markdown(termo_html, unsafe_allow_html=True)

consentimento = st.radio("Marcando a opção 'Sim' a seguir, você autoriza o tratamento dos seus dados.", ["Não", "Sim"], index=0, horizontal=True)

if consentimento == "Não":
    st.warning("⚠️ É necessário aceitar os termos para prosseguir.")
    st.stop()

st.divider()

# --- DADOS PESSOAIS DO RESPONSÁVEL ---
st.subheader("Dados Pessoais do(a) Responsável")
nome_resp = st.text_input("Nome Completo do(a) Responsável *")
vinculo_resp = st.text_input("Vínculo do(a) Responsável (pai, mãe, avó, etc.) *")

col1, col2 = st.columns(2)
with col1:
    cpf_resp = st.text_input("CPF do(a) Responsável *", key="cpf_resp_key", on_change=aplicar_mascaras, max_chars=14, placeholder="000.000.000-00")
    email_resp = st.text_input("E-mail do(a) Responsável *")
with col2:
    telefone_resp = st.text_input("Telefone (WhatsApp) do(a) Responsável *", key="tel_key", on_change=aplicar_mascaras, max_chars=15, placeholder="(00) 00000-0000")
    nasc_resp = st.text_input("Data de Nascimento do(a) Responsável *", key="nasc_resp_key", on_change=aplicar_mascaras, max_chars=10, placeholder="00/00/0000")

st.divider()

# --- DADOS PESSOAIS DO PACIENTE ---
st.subheader("Dados Pessoais do(a) Paciente")
nome_pac = st.text_input("Nome Completo do(a) Paciente *")

col3, col4 = st.columns(2)
with col3:
    cpf_pac = st.text_input("CPF do(a) Paciente *", key="cpf_pac_key", on_change=aplicar_mascaras, max_chars=14, placeholder="000.000.000-00")
with col4:
    nasc_pac = st.text_input("Data de Nascimento do(a) Paciente *", key="nasc_pac_key", on_change=aplicar_mascaras, max_chars=10, placeholder="00/00/0000")

st.divider()

# --- ENDEREÇO ---
st.subheader("Endereço")
cep_input = st.text_input("CEP *", max_chars=10, placeholder="00000-000")

log_auto, bairro_auto, cid_auto, uf_auto = "", "", "", "SC"

if cep_input:
    dados_cep = buscar_cep(cep_input)
    if dados_cep:
        log_auto = dados_cep.get("logradouro", "")
        bairro_auto = dados_cep.get("bairro", "")
        cid_auto = dados_cep.get("localidade", "")
        uf_auto = dados_cep.get("uf", "")

rua = st.text_input("Logradouro (Rua/Avenida) *", value=log_auto)
comp = st.text_input("Número e Complemento *")

col5, col6 = st.columns(2)
with col5:
    bairro_f = st.text_input("Bairro *", value=bairro_auto)
    cidade_f = st.text_input("Cidade *", value=cid_auto)
with col6:
    idx_uf = ESTADOS_BR.index(uf_auto) if uf_auto in ESTADOS_BR else 0
    uf_f = st.selectbox("Estado (UF) *", ESTADOS_BR, index=idx_uf)

st.divider()

# --- COMPLEMENTARES ---
st.subheader("Informações Complementares")
escolaridade = st.selectbox("Escolaridade do(a) Paciente *", OPCOES_ESCOLARIDADE)
encaminhamento = st.text_input("Possui encaminhamento? (Informe o solicitante) *")
demanda = st.text_area("Descreva sua demanda (motivo da avaliação) *", height=100)

if st.button("Enviar Formulário"):
    # Validação atualizada
    campos_obrigatorios = [
        nome_resp, vinculo_resp, cpf_resp, email_resp, telefone_resp, nasc_resp,
        nome_pac, cpf_pac, nasc_pac, cep_input, rua, comp, bairro_f, cidade_f, 
        encaminhamento, demanda
    ]
    
    if escolaridade == "Selecione..." or any(not str(v).strip() for v in campos_obrigatorios):
        st.error("Por favor, preencha todos os campos obrigatórios (*).")
    else:
        dados_finais = {
            "Data de Registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Consentimento": consentimento,
            "Nome do(a) Responsável": nome_resp,
            "Vínculo": vinculo_resp,
            "CPF do(a) Responsável": cpf_resp,
            "E-mail": email_resp,
            "Telefone": telefone_resp,
            "Nascimento do(a) Responsável": nasc_resp,
            "Nome do(a) Paciente": nome_pac,
            "CPF do(a) Paciente": cpf_pac,
            "Nascimento do(a) Paciente": nasc_pac,
            "CEP": cep_input,
            "Endereço Completo": f"{rua}, {comp} - {bairro_f}. {cidade_f}/{uf_f}",
            "Escolaridade do Paciente": escolaridade,
            "Encaminhamento": encaminhamento,
            "Demanda": demanda
        }
        
        if enviar_email_triagem(dados_finais):
            try:
                planilha_triagem.append_row(list(dados_finais.values()))
                st.session_state.enviado = True
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
        else:
            st.error("Erro no envio do e-mail. Tente novamente.")
