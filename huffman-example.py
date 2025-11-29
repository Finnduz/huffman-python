from huffman import HuffmanTree


def main():
    print("=== Huffman-Baum Demo ===\n")

    text = "MISSISSIPPI"
    print(f"Original-Text: {text}")
    print(f"Länge: {len(text)} Zeichen\n")

    tree = HuffmanTree()
    tree.build_from_text(text)

    tree.print_code_table()
    print()

    encoded = tree.encode_text(text)
    print(f"Encodierter Text: {encoded}")
    print(f"Länge: {len(encoded)} Bits")
    print(f"Kompressionsrate: {len(encoded) / (len(text) * 8) * 100:.1f}%\n")

    print("=== Einzelnes Encoding ===")
    for char in set(text):
        code = tree.encode(char)
        print(f"'{char}' -> {code}")
    print()

    print("=== Bit-für-Bit Decoding ===")
    tree.reset_decoder()
    decoded_chars = []
    for i, bit in enumerate(encoded):
        ok, char = tree.decode(bit)
        if ok:
            print(f"Bit {i}: '{bit}' -> Zeichen gefunden: '{char}'")
            decoded_chars.append(char)
        else:
            print(f"Bit {i}: '{bit}' -> noch kein Zeichen")

    decoded_text = ''.join(decoded_chars)
    print(f"\nDecodierter Text: {decoded_text}")
    print(f"Korrekt: {decoded_text == text}")


if __name__ == "__main__":
    main()
