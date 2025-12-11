# Mitologia Grega: Grafo de Conhecimento

Projeto feito para a cadeira de Algoritmos e Estruturas de Dados.
Consiste na implementação da estrutura de Grafo + Métodos de manipulação e análise de grafos, para a construção de um Grafo de Conhecimento.
Além disso, a visualização e interação com o grafo é feita por meio da biblioteca PyVis + interface em Streamlit.

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/DaveOlivae/Greek_Mythology_KnowledgeGraph.git
```

2. Crie um ambiente virtual e ative:
```bash
# no linux
python -m venv mitologia

# ativar
source mitologia/bin/activate
```
3. Instala as Dependências:
```bash
pip install -r requirements.txt
```

4. Execute o Projeto
```bash
streamlit run app.py
```

## Base de Dados

O Grafo de Conhecimento foi feito com base nos personagens e relações da mitologia greco-romana.
Os possíveis tipos de nós (entidades) são:
- Deus/Deusa
- Titã/Titanide
- Herói/Heroína
- Humano/Humana

E os possíveis tipos de relação são:
- Pai de (direcionada)
- Mae de (direcionada)
- Casados (bidirecional)
- Amantes (bidirecional)

### Métodos de Manipulação
É possível realizar as seguintes manipulações no Grafo:
- Adicionar/Remover nós (entidades)
- Criar/Remover arestas (relacionamentos)
- Calcular o grau de um nó.
