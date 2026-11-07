"""Tests für die Huffman-Kodierung in huffman.py."""

from pathlib import Path

import pytest

from huffman import HuffmanTree

FAUST_PFAD = Path(__file__).resolve().parent.parent / "goethe_faust_i.txt"


def _roundtrip(text: str) -> None:
    """Baut den Baum aus ``text`` und prüft decode_text(encode_text(text)) == text."""
    baum = HuffmanTree()
    baum.build_from_text(text)
    assert baum.decode_text(baum.encode_text(text)) == text


def _assert_präfixfrei(code_tabelle: dict[str, str]) -> None:
    """Prüft, dass die Codes nicht leer und paarweise präfixfrei sind."""
    codes = list(code_tabelle.values())
    assert codes, "Code-Tabelle darf nicht leer sein"
    for code in codes:
        assert code, "Code darf nicht leer sein"
        assert set(code) <= {"0", "1"}

    for i, a in enumerate(codes):
        for j, b in enumerate(codes):
            if i != j:
                assert not b.startswith(a), f"{a!r} ist Präfix von {b!r}"


def test_roundtrip_mississippi():
    """Prüft den Roundtrip für den Demo-Text MISSISSIPPI."""
    _roundtrip("MISSISSIPPI")


def test_roundtrip_einzelnes_zeichen():
    """Prüft den Roundtrip für einen Text aus einem einzigen Zeichen."""
    _roundtrip("aaaa")


def test_roundtrip_faust():
    """Prüft den Roundtrip für den vollständigen Faust-Text (UTF-8)."""
    text = FAUST_PFAD.read_text(encoding="utf-8")
    assert text
    _roundtrip(text)


def test_codetabelle_ist_präfixfrei():
    """Prüft, dass die Code-Tabelle ein präfixfreier Code ist."""
    for text in ("MISSISSIPPI", "aaaa"):
        baum = HuffmanTree()
        baum.build_from_text(text)
        tabelle = baum.get_code_table()
        assert set(tabelle) == set(text)
        _assert_präfixfrei(tabelle)


def test_encode_unbekanntes_zeichen():
    """Prüft, dass encode() für ein Zeichen außerhalb des Baums ValueError wirft."""
    baum = HuffmanTree()
    baum.build_from_text("MISSISSIPPI")
    with pytest.raises(ValueError, match="nicht im Huffman-Baum"):
        baum.encode("X")


def test_leerer_text():
    """Prüft, dass ein leerer Text ValueError wirft."""
    baum = HuffmanTree()
    with pytest.raises(ValueError, match="Text darf nicht leer sein"):
        baum.build_from_text("")


def test_leeres_häufigkeitsdictionary():
    """Prüft, dass ein leeres Häufigkeiten-Dictionary ValueError wirft."""
    baum = HuffmanTree()
    with pytest.raises(ValueError, match="Häufigkeiten-Dictionary darf nicht leer sein"):
        baum.build_from_frequencies({})


@pytest.mark.parametrize("bit", ["2", "x"])
def test_decode_ungültiges_bit(bit: str):
    """Prüft, dass decode() bei einem Bit ungleich '0' oder '1' ValueError wirft."""
    baum = HuffmanTree()
    baum.build_from_text("AB")
    with pytest.raises(ValueError, match="Bit muss '0' oder '1' sein"):
        baum.decode(bit)


@pytest.mark.parametrize("bit", ["0", "1"])
def test_decode_nicht_initialisierter_baum(bit: str):
    """Prüft, dass decode() ohne aufgebauten Baum ValueError wirft."""
    baum = HuffmanTree()
    with pytest.raises(ValueError, match="Baum ist nicht initialisiert"):
        baum.decode(bit)


def test_bitweises_decodieren():
    """Prüft bitweises decode(): Zwischenzustand, Blatt und Reset zur Wurzel.

    Mitten im Code ist das Ergebnis (False, None). Am Blatt liefert decode()
    (True, Zeichen) und setzt den Decoder danach auf die Wurzel zurück.
    """
    text = "MISSISSIPPI"
    baum = HuffmanTree()
    baum.build_from_text(text)
    tabelle = baum.get_code_table()

    zeichen = max(tabelle, key=lambda z: len(tabelle[z]))
    code = tabelle[zeichen]
    assert len(code) >= 2

    baum.reset_decoder()
    for bit in code[:-1]:
        assert baum.decode(bit) == (False, None)
        assert baum.current_node is not baum.root

    assert baum.decode(code[-1]) == (True, zeichen)
    assert baum.current_node is baum.root

    # Derselbe Code noch einmal: der Reset muss an der Wurzel gegriffen haben.
    for bit in code[:-1]:
        assert baum.decode(bit) == (False, None)
    assert baum.decode(code[-1]) == (True, zeichen)
    assert baum.current_node is baum.root

    # Vollständiger Bitstrom: nach jedem Zeichen steht der Decoder an der Wurzel.
    baum.reset_decoder()
    gefunden = []
    for bit in baum.encode_text(text):
        ok, char = baum.decode(bit)
        if ok:
            gefunden.append(char)
            assert baum.current_node is baum.root
        else:
            assert char is None
            assert baum.current_node is not baum.root

    assert "".join(gefunden) == text
    assert baum.current_node is baum.root


def test_faust_kürzer_als_8_bit_pro_zeichen():
    """Prüft, dass die Faust-Kodierung kürzer als 8 Bit pro Zeichen ist."""
    text = FAUST_PFAD.read_text(encoding="utf-8")
    baum = HuffmanTree()
    baum.build_from_text(text)
    kodiert = baum.encode_text(text)
    assert len(kodiert) < len(text) * 8
    _assert_präfixfrei(baum.get_code_table())
