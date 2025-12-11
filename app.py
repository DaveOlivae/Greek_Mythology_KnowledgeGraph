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
st.sidebar.header("Controles")
menu = st.sidebar.radio("Ação", ["Adicionar Entidade", "Remover Entidade", "Adicionar Relação", "Remover Relação", "Buscar Caminho"])

if menu == "Adicionar Entidade":
    with st.sidebar.form("add_node"):
        nome = st.text_input("Nome")
        tipo = st.selectbox("Tipo", ["Deus", "Deusa", "Heroi", "Humano", "Humana"])
        local = st.text_input("Localização", placeholder="Ex: Olimpo, Tebas")

        btn = st.form_submit_button("Salvar")

        if btn and nome:
            props = {}
            if local:
                props["local"] = local.strip()

            if grafo.add_node(nome, tipo, props):
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

elif menu == "Remover Relação":
    st.sidebar.subheader("Desfazer Conexão")
    
    lista_nos = list(grafo.nodes.keys())
    
    # 1. Escolha a Origem
    origem = st.sidebar.selectbox("Origem (Quem?)", lista_nos)
    
    # 2. Lógica para filtrar o Destino
    # pegamos apenas os vizinhos que saem do no de origem
    vizinhos = grafo.get_neighbours_out(origem) 
    lista_vizinhos = list(vizinhos.keys())
    
    if not lista_vizinhos:
        st.sidebar.warning(f"{origem} não tem relações para remover.")
    else:
        destino = st.sidebar.selectbox("Destino (Com quem?)", lista_vizinhos)
        
        # Mostra qual é a relação atual para o usuário ter certeza
        tipo_relacao = vizinhos[destino]
        st.sidebar.info(f"Relação atual: **{tipo_relacao}**")
        
        # Botão de ação
        if st.sidebar.button("Cortar Relação"):
            if grafo.remove_edge(origem, destino):
                grafo.save_as_json(ARQUIVO_DADOS)
                
                # Mensagem personalizada dependendo se era casamento ou não
                if "CASADOS" in tipo_relacao:
                    st.sidebar.success("Divórcio concluído!")
                else:
                    st.sidebar.success("Relação removida!")
                    
                st.rerun()
            else:
                st.sidebar.error("Erro ao remover.")

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
    st.sidebar.subheader("Deletar Nó")
    
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
             "Humana": "#87CEEB"
             }

    # 1. Copia Nós
    for id, dados in meu_grafo_puro.nodes.items():
        cor = cores.get(dados['type'], "#999999")

        graus = meu_grafo_puro.get_degree(id)
        neighbours_out = meu_grafo_puro.get_neighbours_out(id)
        neighbours_in = meu_grafo_puro.get_neighbours_in(id)

        # config da vizinhanca = vizinhos_saida + vizinhos_entrada
        # formatar a lista dos vizinhos p texto pra botar no hover
        neighbours_out_txt = []
        for neighbour, relation in neighbours_out.items():
            neighbours_out_txt.append(f" - {neighbour} ({relation})") 

        # junta tudo numa string so
        if neighbours_out_txt:
            str_neighbours_out = "\n".join(neighbours_out_txt)
        else:
            str_neighbours_out = " - (Nenhuma conexão)"

        neighbours_in_txt = []
        for neighbour, relation in neighbours_in.items():
            neighbours_in_txt.append(f" - {neighbour} ({relation})") 

        if neighbours_in_txt:
            str_neighbours_in = "\n".join(neighbours_in_txt)
        else:
            str_neighbours_in = " - (Nenhuma conexão)"

        # texto final que vai aparecer no hover
        tooltip_text = (
            f"=== {id.upper()} ===\n"
            f"Tipo: {dados['type']}\n"
            f"--------------------------\n"
            f"[ESTATÍSTICAS]\n"
            f"Entrada: {graus['entrada']} | Saída: {graus['saida']}\n"
            f"Total: {graus['total']}\n"
            f"--------------------------\n"
            f"[CONEXÕES]\n"
            f"Entrada:\n"
            f"{str_neighbours_in}\n"
            f"Saída\n"
            f"{str_neighbours_out}"
        ) 

        G_visual.add_node(
            id, 
            label=id, 
            title=tooltip_text, 
            color=cor,
            size=25,
        )
    
    # 2. Copia Arestas
    # conjunto pra guardar as arestas ja vistas
    arestas_processadas = set()

    for origem, vizinhos in meu_grafo_puro.adjacency.items():
        for destino, relacao in vizinhos.items():

            # uma conexao eh a mesma independente da ordem origem-destino
            # isso eh util para desenhar uma relacao bidirecional
            chave_conexao = frozenset([origem, destino])

            if chave_conexao in arestas_processadas:
                continue

            tem_volta = False
            vizinhos_destino = meu_grafo_puro.adjacency.get(destino, {})

            if origem in vizinhos_destino and vizinhos_destino[origem] == relacao:
                tem_volta = True

            # desenha uma seta com duas pontas para uma relacao bidirecional 
            if tem_volta:
                G_visual.add_edge(
                    origem, destino, 
                    label=relacao, 
                    arrows="to;from", 
                    font={'face': 'Arial', 'align': 'middle', 'size': 30}
                )
                arestas_processadas.add(chave_conexao)
            else:
                G_visual.add_edge(
                    origem, 
                    destino, 
                    label=relacao,
                    font={'face': 'Arial', 'align': 'middle', 'size': 30}
                )

    # 3. Gera PyVis
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.from_nx(G_visual)
    
    opcoes = {
        "nodes": {
            "font": {
                "size": 35, 
                "face": 'Arial'
            }
        },
        "edges": {
            "smooth": False,
            "color": {"color": "#444444"},
            "font": {"align": "middle", "strokeWidth": 0}},
        "physics": {
            "solver": "repulsion",
            "repulsion": {"nodeDistance": 250, "springLength": 250}
        }
    }

    net.set_options(json.dumps(opcoes))
   
    net.save_graph(ARQUIVO_HTML)
    
    with open(ARQUIVO_HTML, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=650)


# ajeitar a filtragem de nos
st.sidebar.markdown("---")
st.sidebar.subheader("Filtrar Mapa")

# essa parte ve quais locais existem nos dados
all_places = set()
for data in grafo.nodes.values():
    if "local" in data.get("props", {}):
        all_places.add(data["props"]["local"])

filter_options = ["Todos"] + sorted(list(all_places))

choose_place = st.sidebar.selectbox("Mostrar apenas região:", filter_options)

if choose_place == "Todos":
    st.subheader(f"Grafo completo ({len(grafo.nodes)}) entidades")
    desenhar_grafo(grafo)
else:
    subgrafo = grafo.filter_by_prop("local", choose_place)

    st.subheader(f"Região: {choose_place} ({len(subgrafo.nodes)}) entidades")

    if len(subgrafo.nodes) == 0:
        st.warning(f"Ninguém foi encontrado em {choose_place}")
    else:
        desenhar_grafo(subgrafo)

with st.expander("Ver Estrutura de Dados Interna (Dict Python)"):
    st.write("Nós:", grafo.nodes)
    st.write("Adjacência:", grafo.adjacency)