import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# --- Configuração da Página ---
st.set_page_config(page_title="SIGA-Eventos", layout="wide")

# --- Estado Inicial da Aplicação ---
def initialize_state():
    """Inicializa o session_state para manter os dados durante a execução."""
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'login'
    
    if 'user_sub_view' not in st.session_state:
        st.session_state.user_sub_view = 'calendar'
        
    if 'admin_sub_view' not in st.session_state:
        st.session_state.admin_sub_view = 'dashboard'

    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = datetime.now().year
        
    if 'selected_month' not in st.session_state:
        st.session_state.selected_month = datetime.now().month

    if 'admin_dashboard_period' not in st.session_state:
        st.session_state.admin_dashboard_period = 'Mês'

    if 'rooms' not in st.session_state:
        st.session_state.rooms = pd.DataFrame([
            {'id': 1, 'Nome': 'Sala 1', 'Capacidade': 10, 'Status': 'Ativa'},
            {'id': 2, 'Nome': 'Auditório', 'Capacidade': 50, 'Status': 'Ativa'},
            {'id': 3, 'Nome': 'Sala 2', 'Capacidade': 8, 'Status': 'Inativa'},
        ])
    
    if 'show_room_modal' not in st.session_state:
        st.session_state.show_room_modal = False
        
    if 'editing_room_id' not in st.session_state:
        st.session_state.editing_room_id = None

# --- Funções de Renderização das Views ---

def render_login_page():
    """Exibe a tela de login."""
    st.title("SIGA-Eventos")
    st.subheader("Sistema Integrado de Gestão de Agendamentos")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="email@gmail.com")
        password = st.text_input("Senha", type="password", placeholder="*******")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if email.lower().strip() == 'admin@email.com':
                st.session_state.current_view = 'admin'
                st.session_state.admin_sub_view = 'dashboard'
                st.rerun()
            elif email.strip() != '':
                st.session_state.user_email = email
                st.session_state.current_view = 'user'
                st.session_state.user_sub_view = 'calendar'
                st.rerun()
            else:
                st.error("Por favor, insira um e-mail válido.")

def render_user_view():
    """Exibe a view do usuário comum."""
    st.markdown('<style>div[data-testid="stToolbar"] {visibility: hidden;}</style>', unsafe_allow_html=True)
    
    # --- Header ---
    col1, col2, col3 = st.columns([2, 5, 2])
    with col1:
        st.header("SIGA-Eventos")
    with col2:
        selected = st.radio(
            "Navegação", ["Início", "Meus Agendamentos"],
            horizontal=True, label_visibility="collapsed"
        )
        if selected == "Início":
            st.session_state.user_sub_view = 'calendar'
        else:
            st.session_state.user_sub_view = 'bookings'
    with col3:
        if st.button("Sair"):
            st.session_state.current_view = 'login'
            st.rerun()

    st.markdown("---")

    # --- Conteúdo da Sub-view ---
    if st.session_state.user_sub_view == 'calendar':
        render_user_calendar()
    else:
        render_user_bookings()

def render_user_calendar():
    """Exibe o calendário de agendamentos."""
    st.subheader("Painel de Agendamento")
    
    # --- Filtros ---
    col1, col2, col3, col4 = st.columns(4)
    meses = {i+1: calendar.month_name[i+1] for i in range(12)}
    anos = list(range(datetime.now().year - 5, datetime.now().year + 6))
    
    st.session_state.selected_month = col1.selectbox("Mês", options=list(meses.keys()), format_func=lambda x: meses[x], index=st.session_state.selected_month - 1)
    st.session_state.selected_year = col2.selectbox("Ano", options=anos, index=anos.index(st.session_state.selected_year))
    col3.selectbox("Sala", options=["Todas as Salas", "Sala 1", "Sala 2", "Auditório"])
    
    st.markdown(f"### {meses[st.session_state.selected_month]} {st.session_state.selected_year}")

    # --- Calendário (simulado) ---
    dias_semana = ["Horário"] + list(calendar.day_abbr)[1:] + [list(calendar.day_abbr)[0]]
    horarios = [f"{h:02d}:00" for h in range(8, 17)]
    
    cal_data = {dia: ["Livre"] * len(horarios) for dia in dias_semana}
    cal_data["Horário"] = horarios
    
    st.dataframe(pd.DataFrame(cal_data), use_container_width=True)
    st.button("Agendar Novo Evento")


def render_user_bookings():
    """Exibe a lista de agendamentos do usuário."""
    st.subheader("Meus Agendamentos")
    data = {
        "Título do Evento": ["Reunião de Alinhamento Semanal", "Apresentação de Projeto"],
        "Sala": ["Sala 1", "Auditório"],
        "Data": ["10/10/2025", "15/10/2025"],
        "Horário": ["14:00 - 15:00", "10:00 - 11:30"]
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True)


def render_admin_view():
    """Exibe a view do administrador."""
    st.markdown('<style>div[data-testid="stToolbar"] {visibility: hidden;}</style>', unsafe_allow_html=True)

    # --- Header ---
    col1, col2, col3 = st.columns([3, 4, 2])
    with col1:
        st.header("SIGA-Eventos (Admin)")
    with col2:
        selected = st.radio(
            "Navegação Admin", ["Histórico das salas", "Gerenciar Salas"],
            horizontal=True, label_visibility="collapsed"
        )
        if selected == "Histórico das salas":
            st.session_state.admin_sub_view = 'dashboard'
        else:
            st.session_state.admin_sub_view = 'rooms'
    with col3:
        if st.button("Sair"):
            st.session_state.current_view = 'login'
            st.rerun()
            
    st.markdown("---")

    # --- Conteúdo da Sub-view ---
    if st.session_state.admin_sub_view == 'dashboard':
        render_admin_dashboard()
    else:
        render_admin_rooms()
        
def render_admin_dashboard():
    """Exibe o painel de controle do admin."""
    st.subheader("Controle de utilização")
    
    # --- KPIs ---
    col1, col2, col3 = st.columns(3)
    total_salas_ativas = len(st.session_state.rooms[st.session_state.rooms['Status'] == 'Ativa'])
    col1.metric("Total de Salas Ativas", total_salas_ativas)
    col2.metric("Eventos Hoje", "12")
    col3.metric("Taxa de Ocupação", "67%")

    st.markdown("---")
    
    # --- Gráfico ---
    st.subheader("Utilização por Sala")
    
    periodo = st.radio("Filtrar período", ["Dia", "Semana", "Mês"], horizontal=True, index=2)
    st.session_state.admin_dashboard_period = periodo
    
    chart_data = {
        "Mês": {'Sala': ['Sala 1', 'Sala 2', 'Auditório'], 'Agendamentos': [40, 25, 60]},
        "Semana": {'Sala': ['Sala 1', 'Sala 2', 'Auditório'], 'Agendamentos': [10, 8, 15]},
        "Dia": {'Sala': ['Sala 1', 'Sala 2', 'Auditório'], 'Agendamentos': [2, 1, 3]},
    }
    
    df_chart = pd.DataFrame(chart_data[st.session_state.admin_dashboard_period])
    
    fig = px.bar(df_chart, x='Agendamentos', y='Sala', orientation='h', title=f"Agendamentos por Sala ({st.session_state.admin_dashboard_period})")
    st.plotly_chart(fig, use_container_width=True)

def render_admin_rooms():
    """Exibe a tela de gerenciamento de salas."""
    st.subheader("Gerenciar Salas")
    
    if st.button("Adicionar Sala"):
        st.session_state.editing_room_id = None
        st.session_state.show_room_modal = True

    # --- Modal para Adicionar/Editar Sala ---
    if st.session_state.show_room_modal:
        with st.form("room_form"):
            st.subheader("Adicionar/Editar Sala")
            
            nome_default = ""
            capacidade_default = 1
            
            if st.session_state.editing_room_id:
                room_data = st.session_state.rooms[st.session_state.rooms['id'] == st.session_state.editing_room_id].iloc[0]
                nome_default = room_data['Nome']
                capacidade_default = room_data['Capacidade']

            novo_nome = st.text_input("Nome da Sala", value=nome_default)
            nova_capacidade = st.number_input("Capacidade", min_value=1, value=capacidade_default)

            submitted = st.form_submit_button("Salvar")
            if submitted:
                if st.session_state.editing_room_id: # Editando
                    idx = st.session_state.rooms.index[st.session_state.rooms['id'] == st.session_state.editing_room_id][0]
                    st.session_state.rooms.at[idx, 'Nome'] = novo_nome
                    st.session_state.rooms.at[idx, 'Capacidade'] = nova_capacidade
                else: # Adicionando
                    new_id = max(st.session_state.rooms['id']) + 1 if not st.session_state.rooms.empty else 1
                    nova_sala = pd.DataFrame([{'id': new_id, 'Nome': novo_nome, 'Capacidade': nova_capacidade, 'Status': 'Ativa'}])
                    st.session_state.rooms = pd.concat([st.session_state.rooms, nova_sala], ignore_index=True)
                
                st.session_state.show_room_modal = False
                st.rerun()

    # --- Tabela de Salas ---
    df_display = st.session_state.rooms.copy()
    df_display['Ações'] = ""
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # --- Lógica para botões na tabela ---
    cols = st.columns(len(st.session_state.rooms))
    for i, row in st.session_state.rooms.iterrows():
        with cols[i]:
            if st.button(f"Editar", key=f"edit_{row['id']}"):
                st.session_state.editing_room_id = row['id']
                st.session_state.show_room_modal = True
                st.rerun()
            
            toggle_text = "Desativar" if row['Status'] == 'Ativa' else 'Ativar'
            if st.button(toggle_text, key=f"toggle_{row['id']}"):
                st.session_state.rooms.at[i, 'Status'] = 'Inativa' if row['Status'] == 'Ativa' else 'Ativa'
                st.rerun()


# --- Ponto de Entrada da Aplicação ---

initialize_state()

if st.session_state.current_view == 'login':
    render_login_page()
elif st.session_state.current_view == 'user':
    render_user_view()
elif st.session_state.current_view == 'admin':
    render_admin_view()
