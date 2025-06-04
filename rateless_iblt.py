import hashlib
from collections import defaultdict

class CodedSymbol:
    """
    Reprezentuje zakodowany symbol w rateless IBLT.

    Atrybuty:
        key_sum (int): XOR sum kluczy zakodowanych w tym symbolu.
        count (int): Różnica liczby wstawień i usunięć.
    """
    def __init__(self):
        self.key_sum = 0
        self.count = 0
    
    def __xor__(self, other):
        """
        Zwraca XOR tego symbolu z innym CodedSymbol.

        Args:
            other (CodedSymbol): Symbol do połączenia.

        Returns:
            CodedSymbol: Nowy symbol będący wynikiem operacji XOR.
        """
        result = CodedSymbol()
        result.key_sum = self.key_sum ^ other.key_sum
        result.count = self.count - other.count
        return result

class RatelessIBLT:
    """
    Implementacja Rateless IBLT do różnicowania zbiorów danych.

    Args:
        alpha (float): Parametr kontrolujący prawdopodobieństwo mapowania.
    """
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.data = []
        self.known_keys = {}
        self.mapping_cache = defaultdict(set)
    
    def _key_to_int(self, key):
        """
        Przekształca klucz tekstowy na liczbę całkowitą przy użyciu SHA-256.

        Args:
            key (str): Klucz do przekształcenia.

        Returns:
            int: Wartość haszu jako liczba całkowita.
        """
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)
    
    def insert(self, key):
        """
        Wstawia klucz do IBLT.

        Args:
            key (str): Klucz do wstawienia.
        """
        self.data.append((key))
        key_int = self._key_to_int(key)
        self.known_keys[key_int] = key
    
    def should_map(self, key, index):
        """
        Decyduje, czy dany klucz powinien być zmapowany do danego indeksu.

        Args:
            key (str): Klucz do sprawdzenia.
            index (int): Indeks symbolu.

        Returns:
            bool: True jeśli powinien być zmapowany, False w przeciwnym razie.
        """
        if index in self.mapping_cache[key]:
            return True
        h = hashlib.sha256(f"{key}:{index}".encode('utf-8')).hexdigest()
        r = int(h, 16) / (2**256)
        rho = 1 / (1 + self.alpha * index)
        if r < rho:
            self.mapping_cache[key].add(index)
            return True
        return False
    
    def generate_symbol(self, index):
        """
        Generuje zakodowany symbol dla danego indeksu.

        Args:
            index (int): Indeks symbolu.

        Returns:
            CodedSymbol: Zakodowany symbol z danymi.
        """
        symbol = CodedSymbol()
        for key in self.data:
            if self.should_map(key, index):
                key_int = self._key_to_int(key)
                symbol.key_sum ^= key_int
                symbol.count += 1
        return symbol
        
    def subtract(self, other, max_symbols):
        """
        Oblicza różnicę symboli między dwoma rateless IBLT.

        Args:
            other (RatelessIBLT): Druga instancja ratelesss IBLT.
            max_symbols (int): Liczba symboli do wygenerowania i porównania.
        """
        self.symbols = []
        for i in range(max_symbols):
            a = self.generate_symbol(i)
            b = other.generate_symbol(i)
            c = a ^ b
            self.symbols.append(c)
    def list_entries(self):
        """
        Odtwarza różnice (dodane i usunięte klucze) pomiędzy rateless IBLT.

        Returns:
            tuple: (lista dodanych kluczy, lista usuniętych kluczy)
        """
        entries = []
        deletions = []
        changed = True
        while changed:
            changed = False
            for i, cell in enumerate(self.symbols):
                if abs(cell.count) == 1:
                    key_int = cell.key_sum
                    key_str = self.known_keys.get(key_int)
                    if key_str is None:
                        continue
                    if cell.count == 1:
                        entries.append((key_str))
                    else:
                        deletions.append((key_str))

                    for j in range(len(self.symbols)):
                        if self.should_map(key_str, j):
                            self.symbols[j].key_sum ^= key_int
                            self.symbols[j].count -= cell.count

                    changed = True
                    break
        return entries, deletions
    


iblt_A = RatelessIBLT()
iblt_A.insert("a")
iblt_A.insert("b")
iblt_A.insert("c")

iblt_B = RatelessIBLT()
iblt_B.insert("b")
iblt_B.insert("c")
iblt_B.insert("d")

iblt_A.known_keys.update(iblt_B.known_keys)

iblt_A.subtract(iblt_B, max_symbols=20)

# odczytanie roznic
inserted, deleted = iblt_A.list_entries()
print("Inserted:", inserted)
print("Deleted:", deleted)
