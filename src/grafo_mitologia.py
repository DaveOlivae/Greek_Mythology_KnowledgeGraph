import json
from collections import deque

class GrafoMitologia:
    def __init__(self):
        # dicionario de nos {nome: atributos}
        self.nodes = {}

        # lista de adjacencia para todos os nos
        self.adjacency = {}
    

    def add_node(self, id, type, props=None):
        """
        Docstring for add_node
        
        :param id: nome do nó 
        :param type: tipo (Deus, Humano, etc) 
        :param props: características da entidade 
        """

        if props is None:
            props = {}

        if id not in self.nodes:
            self.nodes[id] = {"type": type, "props": props}
            self.adjacency[id] = {}
            return True

        return False
    

    def add_edge(self, origin, destiny, relation):
        if origin in self.nodes and destiny in self.nodes:
            self.adjacency[origin][destiny] = relation
            return True
        return False
    

    def remover_no(self, id_no):
        if id_no in self.nodes:
            # 1. Remove o nó e suas propriedades
            del self.nodes[id_no]
            
            # 2. Remove as arestas que SAEM dele (se existirem)
            if id_no in self.adjacency:
                del self.adjacency[id_no]
            
            # 3. Remove as arestas que CHEGAM nele (varredura completa)
            # Precisamos olhar todos os outros nós para ver se alguém apontava para o falecido
            for origem in self.adjacency:
                if id_no in self.adjacency[origem]:
                    del self.adjacency[origem][id_no]
            
            return True
        return False

    
    def get_neighbours(self, id):
        return self.adjacency.get(id, {})
    

    def buscar_caminho_curto(self, inicio, fim):
        """
        Algoritmo BFS (Busca em Largura) puro para achar o menor caminho.
        Retorna uma lista de nós [Zeus, Ares, Harmonia] ou None.
        """
        if inicio not in self.nodes or fim not in self.nodes:
            return None

        fila = deque([(inicio, [inicio])]) # Tupla (Vertice Atual, Caminho Percorrido)
        visitados = set([inicio])

        while fila:
            (vertice, caminho) = fila.popleft()
            
            # Chegamos?
            if vertice == fim:
                return caminho
            
            # Pega vizinhos do dicionário de adjacência
            for vizinho in self.adjacency[vertice]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append((vizinho, caminho + [vizinho]))
    

    def load_from_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for ent in data.get("entities", []):
                self.add_node(ent["id"], ent["type"], ent.get("props", {}))

            for rel in data.get("relations", []):
                self.add_edge(rel["origin"], rel["destiny"], rel["relation"])
            
            return True
        except FileNotFoundError:
            return False
        
    
    def save_as_json(self, caminho_arquivo):
        dados_export = {"entities": [], "relations": []}
        
        # Converte nós
        for id_no, dados in self.nodes.items():
            dados_export["entities"].append({
                "id": id_no,
                "type": dados["type"],
                "props": dados["props"]
            })
            
        # Converte arestas (percorre a lista de adjacência)
        for origem, destinos in self.adjacency.items():
            for destino, relacao in destinos.items():
                dados_export["relations"].append({
                    "origin": origem,
                    "destiny": destino,
                    "relation": relacao
                })
                
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_export, f, indent=4)