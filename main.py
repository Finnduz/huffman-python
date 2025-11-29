from collections import Counter
import heapq
from graphviz import Digraph
import json

# 1. Text einlesen und Häufigkeiten bestimmen
with open('goethe_faust_i.txt', 'r', encoding='utf-8') as f:
    text = f.read().lower()

freq = Counter(text)
print("Top 5 Zeichen:", freq.most_common(5))
print("Einzigartige Zeichen:", len(freq))

# 2. Huffman-Knoten
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char          # None bei inneren Knoten
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# 3. Huffman-Baum aus genau EINER Priority Queue bauen
def build_huffman_tree(freq_dict):
    heap = [HuffmanNode(ch, fr) for ch, fr in freq_dict.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        # Spezialfall: nur ein Zeichen
        only = heapq.heappop(heap)
        root = HuffmanNode(None, only.freq)
        root.left = only
        return root

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        parent = HuffmanNode(None, n1.freq + n2.freq)
        parent.left, parent.right = n1, n2
        heapq.heappush(heap, parent)

    return heap[0]   # WURZEL

root = build_huffman_tree(freq)
print("Gesamtzeichen:", root.freq)

# 3b. Baum nach JSON serialisieren
def tree_to_dict(node):
    if node is None:
        return None
    return {
        "char": node.char,          # kann None sein
        "freq": node.freq,
        "left": tree_to_dict(node.left),
        "right": tree_to_dict(node.right),
    }

tree_dict = tree_to_dict(root)

with open("huffman_faust_i_tree.json", "w", encoding="utf-8") as f:
    json.dump(tree_dict, f, ensure_ascii=False, indent=2)

print("Baum als JSON gespeichert: huffman_faust_i_tree.json")

# 4. Graphviz: EIN Digraph, rekursiv von der Wurzel aus
dot = Digraph(comment='Huffman Baum Faust I', format='png')
dot.attr(rankdir='TB', fontsize='10', fontname='Arial')

def add_to_graph(node, node_id='root'):
    # Label
    if node.char is None:
        label = f'{node.freq}'
        dot.node(node_id, label, shape='circle', style='filled', fillcolor='yellow')
    else:
        ch = node.char.replace('\n', '\\n').replace('"', '\\"')
        label = f'"{ch}"\\n{node.freq}'
        dot.node(node_id, label, shape='box', style='filled', fillcolor='lightblue')

    # Kinder
    if node.left:
        left_id = node_id + '0'
        add_to_graph(node.left, left_id)
        dot.edge(node_id, left_id, label='0')
    if node.right:
        right_id = node_id + '1'
        add_to_graph(node.right, right_id)
        dot.edge(node_id, right_id, label='1')

add_to_graph(root)

dot.render('huffman_faust_i', cleanup=True)
print("Baum gespeichert als huffman_faust_i.png")
