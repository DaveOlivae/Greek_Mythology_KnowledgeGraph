import json
from collections import deque

class GrafoMitologia:
    def __init__(self):
        # dicionario de nos {nome: atributos}
        self.nodes = {}

        # lista de adjacencia para todos os nos
        self.adjacency = {}

        # lista das relacoes bidirecionais (pra que a volta seja adicionada automaticamente)
        self.relacoes_bidirecionais = {
            "CASADOS",
            "AMANTES"
        }
    

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
            # adiciona a relacao
            self.adjacency[origin][destiny] = relation

            if relation in self.relacoes_bidirecionais:
                self.adjacency[destiny][origin] = relation

            return True
        return False

    def remove_edge(self, origin, destiny):
        """
        Remove a conexão entre dois nós.
        Se a relação for bidirecional (ex: CASADO_COM), remove a volta também.
        """
        # verifica se a conexao existe
        if origin in self.adjacency and destiny in self.adjacency[origin]:
            
            # Guarda o nome da relação antes de deletar (usado pra remover bidirecional)
            relation = self.adjacency[origin][destiny]
            
            # remove a relação de IDA
            del self.adjacency[origin][destiny]
            
            # verifica se precisa remover a VOLTA 
            
            if relation in self.relacoes_bidirecionais:
                # checa se o destino tambem aponta de volta com a mesma relation
                if destiny in self.adjacency and origin in self.adjacency[destiny]:
                    if self.adjacency[destiny][origin] == relation:
                        del self.adjacency[destiny][origin]
            
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
    
    
    def get_degree(self, id):
        if id not in self.nodes:
            return None
        
        out_degree = len(self.adjacency.get(id, {}))

        in_degree = 0
        for origin, neighbours in self.adjacency.items():
            if id in neighbours:
                in_degree += 1
        
        total_degree = out_degree + in_degree

        return {
            "entrada": in_degree,
            "saida": out_degree,
            "total": total_degree
        }
    
    def filter_by_prop(self, prop_key, value):
        """
        cria um subgrafo contendo apenas nos que tem uma determinada propriedade
        ex: local = olimpo
            somente os nos que tem essa propriedade irao para o grafo
        """

        subgraph = GrafoMitologia()

        # esse loop copia os nos que atendem ao criterio
        for id, data in self.nodes.items():

            prop_value = data['props'].get(prop_key)

            # se valor for igual add ao subgrafo
            if prop_value == value:
                subgraph.add_node(id, data['type'], data['props'])

        # esse loop eh pra lidar com as arestas
        # a ideia eh que a relacao so vai ser adicionada se ambos os nos tiverem a mesma prop
        for origin in subgraph.nodes:
            neighbours = self.get_neighbours(origin)

            for destiny, relation in neighbours.items():
                # se o destino nao tiver no subgrafo, entao nao tem a prop, logo nao add
                if destiny in subgraph.nodes:
                    subgraph.add_edge(origin, destiny, relation)

        return subgraph
    

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