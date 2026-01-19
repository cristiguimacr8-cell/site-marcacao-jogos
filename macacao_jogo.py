import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Gestão de Ligas Futebolísticas", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1 { color: #001f3f; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: bold; color: #001f3f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BANCO DE DADOS (Simulação) ---
if 'equipes' not in st.session_state:
    st.session_state.equipes = [
        {"Nome": "Sua Equipa", "Cidade": "Lobito", "Contacto": "admin@meu.com", "ID": 1}
    ]
if 'pedidos_jogos' not in st.session_state:
    st.session_state.pedidos_jogos = []
if 'jogos_confirmados' not in st.session_state:
    st.session_state.jogos_confirmados = []
if 'next_team_id' not in st.session_state:
    st.session_state.next_team_id = 2

st.title("🏆 Plataforma de Gestão de Jogos de Futebol")

# --- MENU PRINCIPAL (TABS) ---
tab1, tab2, tab3, tab4 = st.tabs(["Meu Dashboard", "Cadastrar Equipa", "Pedidos de Jogo", "Área Admin"])

# --- TAB 1: DASHBOARD (VISÃO PÚBLICA) ---
with tab1:
    st.header("Visão Geral da Liga")

    col1, col2, col3 = st.columns(3)
    col1.metric("Equipas Registadas", len(st.session_state.equipes))
    col2.metric("Jogos Confirmados", len(st.session_state.jogos_confirmados))
    col3.metric("Pedidos Pendentes", len(st.session_state.pedidos_jogos))

    st.subheader("Próximos Jogos Confirmados")
    if st.session_state.jogos_confirmados:
        df_confirmados = pd.DataFrame(st.session_state.jogos_confirmados)
        st.dataframe(df_confirmados, use_container_width=True)
    else:
        st.info("Nenhum jogo confirmado para as próximas semanas.")

    st.subheader("Equipas Disponíveis Para Convite")
    df_equipes = pd.DataFrame(st.session_state.equipes)
    st.dataframe(df_equipes[['Nome', 'Cidade']], use_container_width=True)

# --- TAB 2: CADASTRAR EQUIPA (UTILIZADOR ENVIA PEDIDO DE CADASTRO) ---
with tab2:
    st.header("Registar Nova Equipa na Plataforma")
    st.write("Preencha os dados para que outras equipas possam desafiar a sua.")
    with st.form("form_cadastro_equipa"):
        nome_equipa = st.text_input("Nome da Equipa")
        cidade = st.text_input("Cidade/Localização")
        contacto = st.text_input("Contacto (Email/Telefone)")
        submitted_team = st.form_submit_button("Submeter Equipa para Aprovação")

        if submitted_team:
            if nome_equipa and cidade and contacto:
                nova_equipa = {
                    "Nome": nome_equipa,
                    "Cidade": cidade,
                    "Contacto": contacto,
                    "ID": st.session_state.next_team_id
                }
                # Em um sistema real, isso iria para uma área de aprovação
                st.session_state.equipes.append(nova_equipa)
                st.session_state.next_team_id += 1
                st.success(f"Equipa {nome_equipa} registada com sucesso! Você já pode ser desafiado.")
            else:
                st.error("Preencha todos os campos.")

# --- TAB 3: PEDIDOS DE JOGO (UTILIZADOR ENVIA PEDIDO DE JOGO) ---
with tab3:
    st.header("Desafiar Outra Equipa")
    st.write("Envie um pedido de jogo para qualquer equipa registada na nossa liga.")

    # A sua equipa é sempre a primeira
    equipes_disponiveis = [e['Nome'] for e in st.session_state.equipes if e['Nome'] != "Sua Equipa"]

    if equipes_disponiveis:
        with st.form("form_desafio"):
            equipa_adversaria = st.selectbox("Escolha a Equipa Adversária:", equipes_disponiveis)
            data_sugerida = st.date_input("Data Proposta:", min_value=datetime.today())
            local_sugerido = st.text_input("Local Proposto:")
            submitted_challenge = st.form_submit_button("Enviar Pedido de Jogo")

            if submitted_challenge:
                novo_pedido = {
                    "Equipa Desafiante": "Sua Equipa",
                    "Equipa Desafiada": equipa_adversaria,
                    "Data Proposta": str(data_sugerida),
                    "Local": local_sugerido,
                    "Status": "Pendente"
                }
                st.session_state.pedidos_jogos.append(novo_pedido)
                st.info(f"Pedido enviado para {equipa_adversaria}. Aguardando confirmação do administrador.")
    else:
        st.warning("Registe mais equipas para poder desafiá-las.")

# --- TAB 4: ÁREA ADMIN (VOCÊ ORDENA AS MARCAÇÕES) ---
with tab4:
    st.header("🔑 Área do Administrador (Jó)")
    st.subheader("Gerir Pedidos Pendentes")

    if st.session_state.pedidos_jogos:
        for i, pedido in enumerate(st.session_state.pedidos_jogos):
            st.warning(
                f"PEDIDO #{i + 1}: {pedido['Equipa Desafiante']} vs {pedido['Equipa Desafiada']} em {pedido['Data Proposta']}")

            col_admin1, col_admin2, col_admin3 = st.columns(3)
            with col_admin1:
                if st.button(f"✅ Aceitar Pedido #{i + 1}", key=f"aceitar_{i}"):
                    # Move para jogos confirmados
                    pedido['Status'] = "CONFIRMADO"
                    st.session_state.jogos_confirmados.append(pedido)
                    # Remove dos pendentes
                    st.session_state.pedidos_jogos.pop(i)
                    st.success("Jogo confirmado e movido para a lista oficial!")
                    st.rerun()
            with col_admin2:
                if st.button(f"❌ Rejeitar Pedido #{i + 1}", key=f"rejeitar_{i}"):
                    st.session_state.pedidos_jogos.pop(i)
                    st.error("Pedido rejeitado e removido.")
                    st.rerun()
            st.divider()
    else:
        st.info("Nenhum pedido de jogo pendente para aprovação.")

    st.subheader("Limpeza do Sistema")
    if st.button("Limpar TODOS os Registos (Reset Total)", type="secondary"):
        st.session_state.equipes = [{"Nome": "Sua Equipa", "Cidade": "Lobito", "Contacto": "admin@meu.com", "ID": 1}]
        st.session_state.pedidos_jogos = []
        st.session_state.jogos_confirmados = []
        st.success("Sistema resetado.")
        st.rerun()

