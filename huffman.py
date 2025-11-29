import heapq
from typing import Dict, Tuple, Optional


class Node:
    """Repräsentiert einen Knoten im Huffman-Baum."""

    def __init__(self, freq: int, char: Optional[str] = None, left: Optional['Node'] = None, right: Optional['Node'] = None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        """Prüft, ob dieser Knoten ein Blatt ist."""
        return self.left is None and self.right is None

    def __lt__(self, other: 'Node') -> bool:
        """Vergleichsoperator für Priority Queue."""
        return self.freq < other.freq


class HuffmanTree:
    """Huffman-Baum mit Encoding- und Decoding-Funktionalität."""

    def __init__(self):
        self.root: Optional[Node] = None
        self.code_table: Dict[str, str] = {}
        self.current_node: Optional[Node] = None

    def build_from_frequencies(self, freq_dict: Dict[str, int]) -> None:
        """
        Baut den Huffman-Baum aus einem Häufigkeiten-Dictionary auf.

        Args:
            freq_dict: Dictionary mit Zeichen als Keys und Häufigkeiten als Values
        """
        if not freq_dict:
            raise ValueError("Häufigkeiten-Dictionary darf nicht leer sein")

        if len(freq_dict) == 1:
            char = list(freq_dict.keys())[0]
            freq = freq_dict[char]
            self.root = Node(freq, char)
            self.code_table = {char: "0"}
            self.current_node = self.root
            return

        priority_queue = [Node(freq, char) for char, freq in freq_dict.items()]
        heapq.heapify(priority_queue)

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)

            parent = Node(left.freq + right.freq, left=left, right=right)
            heapq.heappush(priority_queue, parent)

        self.root = priority_queue[0]
        self.current_node = self.root
        self._build_code_table()

    def build_from_text(self, text: str) -> None:
        """
        Berechnet Häufigkeiten aus einem Text und baut den Baum auf.

        Args:
            text: Text, aus dem die Häufigkeiten berechnet werden
        """
        if not text:
            raise ValueError("Text darf nicht leer sein")

        freq_dict = {}
        for char in text:
            freq_dict[char] = freq_dict.get(char, 0) + 1

        self.build_from_frequencies(freq_dict)

    def _build_code_table(self) -> None:
        """Erstellt die Code-Tabelle durch Baum-Traversierung."""
        self.code_table = {}

        def traverse(node: Optional[Node], code: str) -> None:
            if node is None:
                return

            if node.is_leaf():
                self.code_table[node.char] = code if code else "0"
            else:
                traverse(node.left, code + "0")
                traverse(node.right, code + "1")

        traverse(self.root, "")

    def encode(self, char: str) -> str:
        """
        Encodiert ein Zeichen zu einem Bitstring.

        Args:
            char: Zu encodierendes Zeichen

        Returns:
            Bitstring als String (z.B. "1011")

        Raises:
            ValueError: Wenn das Zeichen nicht im Baum vorhanden ist
        """
        if char not in self.code_table:
            raise ValueError(f"Zeichen '{char}' ist nicht im Huffman-Baum enthalten")

        return self.code_table[char]

    def encode_text(self, text: str) -> str:
        """
        Encodiert einen ganzen Text zu einem Bitstring.

        Args:
            text: Zu encodierender Text

        Returns:
            Bitstring als String
        """
        return ''.join(self.encode(char) for char in text)

    def decode(self, bit: str) -> Tuple[bool, Optional[str]]:
        """
        Decodiert ein einzelnes Bit. Stateful - wandert durch den Baum.

        Args:
            bit: Ein einzelnes Bit als String ('0' oder '1')

        Returns:
            Tupel (ok, char):
            - ok=False, char=None: Noch kein Blatt erreicht
            - ok=True, char=Zeichen: Blatt erreicht, Decoder wurde zurückgesetzt

        Raises:
            ValueError: Wenn bit nicht '0' oder '1' ist oder Baum nicht initialisiert
        """
        if bit not in ('0', '1'):
            raise ValueError(f"Bit muss '0' oder '1' sein, erhalten: '{bit}'")

        if self.root is None:
            raise ValueError("Baum ist nicht initialisiert")

        if self.current_node is None:
            self.current_node = self.root

        if self.root.is_leaf():
            char = self.root.char
            return (True, char)

        if bit == '0':
            self.current_node = self.current_node.left
        else:
            self.current_node = self.current_node.right

        if self.current_node.is_leaf():
            char = self.current_node.char
            self.current_node = self.root
            return (True, char)

        return (False, None)

    def decode_text(self, bitstring: str) -> str:
        """
        Decodiert einen Bitstring zu einem Text.

        Args:
            bitstring: Bitstring als String (z.B. "10110011")

        Returns:
            Decodierter Text
        """
        self.reset_decoder()
        result = []

        for bit in bitstring:
            ok, char = self.decode(bit)
            if ok:
                result.append(char)

        return ''.join(result)

    def reset_decoder(self) -> None:
        """Setzt den Decoder-Zustand zurück zur Wurzel."""
        self.current_node = self.root

    def get_code_table(self) -> Dict[str, str]:
        """
        Gibt die Code-Tabelle zurück.

        Returns:
            Dictionary mit Zeichen als Keys und Bitstrings als Values
        """
        return self.code_table.copy()

    def print_code_table(self) -> None:
        """Gibt die Code-Tabelle formatiert aus."""
        print("Huffman-Code-Tabelle:")
        print("-" * 30)
        for char, code in sorted(self.code_table.items()):
            display_char = repr(char) if char in ('\n', '\t', ' ') else char
            print(f"{display_char:5s} -> {code}")
