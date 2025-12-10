import os
import streamlit as st
from src.grafo_mitologia import GrafoMitologia 
from pyvis.network import Network
import networkx as nx
import json

# config da pagina
st.set_page_config(page_title="Mitologia Graph", layout="wide")
st.title("Grafo de Conhecimento: Mitologia Grega")

PASTA_DADOS = "data"
ARQUIVO_DADOS = os.path.join(PASTA_DADOS, "dados_mitologia.json")

PASTA_TEMP = "temp"
ARQUIVO_HTML = os.path.join(PASTA_TEMP, "grafo_temp.html")


@st.cache_resource
def get_grafo():
    g = GrafoMitologia()
    g.load_from_json(ARQUIVO_DADOS)
    return g

grafo = get_grafo()

# --- SIDEBAR: ADICIONAR ---
st.sidebar.header("🛠️ Controles")
menu = st.sidebar.radio("Ação", ["Adicionar Entidade", "Adicionar Relação", "Remover Entidade", "Buscar Caminho"])

if menu == "Adicionar Entidade":
    with st.sidebar.form("add_node"):
        nome = st.text_input("Nome")
        tipo = st.selectbox("Tipo", ["Deus", "Deusa", "Heroi", "Humano", "Humana", "Monstro"])
        btn = st.form_submit_button("Salvar")
        if btn and nome:
            if grafo.add_node(nome, tipo):
                grafo.save_as_json(ARQUIVO_DADOS)
                st.success(f"{nome} adicionado!")
                st.rerun()
            else:
                st.error("Já existe!")

elif menu == "Adicionar Relação":
    with st.sidebar.form("add_edge"):
        lista_nos = list(grafo.nodes.keys())
        origem = st.selectbox("Origem", lista_nos)
        destino = st.selectbox("Destino", lista_nos)
        relacao = st.text_input("Relação", value="PAI_DE")
        btn = st.form_submit_button("Conectar")
        if btn:
            grafo.add_edge(origem, destino, relacao)
            grafo.save_as_json(ARQUIVO_DADOS)
            st.success("Conectado!")
            st.rerun()

elif menu == "Buscar Caminho":
    st.sidebar.subheader("Algoritmo BFS")
    lista_nos = list(grafo.nodes.keys())
    inicio = st.sidebar.selectbox("Início", lista_nos)
    fim = st.sidebar.selectbox("Fim", lista_nos, index=1)
    
    if st.sidebar.button("Encontrar Caminho"):
        caminho = grafo.buscar_caminho_curto(inicio, fim)
        if caminho:
            st.sidebar.success(f"Caminho encontrado: {' -> '.join(caminho)}")
        else:
            st.sidebar.error("Não há conexão entre esses nós.")

elif menu == "Remover Entidade":
    st.sidebar.subheader("🗑️ Deletar Nó")
    
    lista_nos = list(grafo.nodes.keys())
    
    if not lista_nos:
        st.sidebar.warning("O grafo está vazio.")
    else:
        no_para_remover = st.sidebar.selectbox("Selecione para excluir", lista_nos)
        
        btn_remover = st.sidebar.button("Excluir Definitivamente", type="primary")
        
        if btn_remover:
            if grafo.remover_no(no_para_remover):
                grafo.save_as_json(ARQUIVO_DADOS)
                st.success(f"'{no_para_remover}' foi removido do mapa!")
                st.rerun()
            else:
                st.error("Erro ao remover.")

# --- VISUALIZAÇÃO (PONTE PARA PYVIS) ---
# converter grafo para visualizacao
def desenhar_grafo(meu_grafo_puro):
    # cria um grafo com NX so pra visualizar
    G_visual = nx.DiGraph()
    
    cores = {"Deus": "#FFD700",
             "Deusa": "#FFD700", 
             "Heroi": "#FF69B4", 
             "Humano": "#87CEEB", 
             "Humana": "#87CEEB",
             "Monstro": "#8B0000"}

    # 1. Copia Nós
    for id_no, dados in meu_grafo_puro.nodes.items():
        cor = cores.get(dados['type'], "#999999")

        G_visual.add_node(id_no, 
                          label=id_no, 
                          title=dados['type'], 
                          color=cor,
                          size=20,
                          font={'face': 'JetBrainsMono Nerd Font', 'size': 30, 'color': 'black'}
                          )
    
    # 2. Copia Arestas
    for origem, vizinhos in meu_grafo_puro.adjacency.items():
        for destino, relacao in vizinhos.items():
            G_visual.add_edge(origem, 
                              destino, 
                              label=relacao,
                              font={'face': 'JetBrainsMono Nerd Font', 'align': 'middle', 'size': 20}
                              )

    # 3. Gera PyVis
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.from_nx(G_visual)
    
    opcoes = {
        "edges": {
            "smooth": False,
            "color": {"color": "#444444"},
            "font": {"align": "middle", "strokeWidth": 0}},
        "physics": {
            "solver": "repulsion",
            "repulsion": {"nodeDistance": 155, "springLength": 135}
        }
    }

    net.set_options(json.dumps(opcoes))
   
    net.save_graph(ARQUIVO_HTML)
    
    with open(ARQUIVO_HTML, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=650)

desenhar_grafo(grafo)

with st.expander("Ver Estrutura de Dados Interna (Dict Python)"):
    st.write("Nós:", grafo.nodes)
    st.write("Adjacência:", grafo.adjacency)