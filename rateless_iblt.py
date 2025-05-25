import hashlib
from collections import defaultdict

class CodedSymbol:
    def __init__(self):
        self.key_sum = 0
        self.value_sum = 0
        self.count = 0
    
    def __xor__(self, other):
        result = CodedSymbol()
        result.key_sum = self.key_sum ^ other.key_sum
        result.value_sum = self.value_sum ^ other.value_sum
        result.count = self.count - other.count
        return result

class RatelessIBLT:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.data = []
        self.known_keys = {}
        self.known_values = {}
        self.mapping_cache = defaultdict(set)
    
    def _key_to_int(self, key):
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)
    
    def insert(self, key, value):
        self.data.append((key, value))
        key_int = self._key_to_int(key)
        value_int = self._key_to_int(value)
        self.known_keys[key_int] = key
        self.known_values[value_int] = value
    
    def should_map(self, key, index):
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
        symbol = CodedSymbol()
        for key, value in self.data:
            if self.should_map(key, index):
                key_int = self._key_to_int(key)
                value_int = self._key_to_int(value)
                symbol.key_sum ^= key_int
                symbol.value_sum ^= value_int
                symbol.count += 1
        return symbol
        
    def subtract(self, other, max_symbols):
        self.symbols = []
        for i in range(max_symbols):
            a = self.generate_symbol(i)
            b = other.generate_symbol(i)
            c = a ^ b
            self.symbols.append(c)
    def list_entries(self):
        entries = []
        deletions = []
        changed = True
        while changed:
            changed = False
            for i, cell in enumerate(self.symbols):
                if abs(cell.count) == 1:
                    key_int = cell.key_sum
                    value_int = cell.value_sum
                    key_str = self.known_keys.get(key_int)
                    value_str = self.known_values.get(value_int)
                    if key_str is None or value_str is None:
                        continue
                    if cell.count == 1:
                        entries.append((key_str, value_str))
                    else:
                        deletions.append((key_str, value_str))

                    for j in range(len(self.symbols)):
                        if self.should_map(key_str, j):
                            self.symbols[j].key_sum ^= key_int
                            self.symbols[j].value_sum ^= value_int
                            self.symbols[j].count -= cell.count

                    changed = True
                    break
        return entries, deletions
    


iblt_A = RatelessIBLT()
iblt_A.insert("a", "val")
iblt_A.insert("b", "val")
iblt_A.insert("c", "val")

iblt_B = RatelessIBLT()
iblt_B.insert("b", "val")
iblt_B.insert("c", "val")
iblt_B.insert("d", "val")

iblt_A.known_keys.update(iblt_B.known_keys)
iblt_A.known_values.update(iblt_B.known_values)

iblt_A.subtract(iblt_B, max_symbols=20)

# odczytanie roznic
inserted, deleted = iblt_A.list_entries()
print("Inserted:", inserted)
print("Deleted:", deleted)
