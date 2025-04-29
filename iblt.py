import hashlib

#Cell(coded symbol) to nasze kodowane symbole, kazdy klucz (source symbol) bedziemy mapowac na hash_count=3 symbole
class Cell:
    def __init__(self):
        self.key_sum = 0
        self.value_sum = 0
        self.count = 0

    def __str__(self):
        return f"Cell(key_sum={self.key_sum}, value_sum={self.value_sum}, count={self.count})"

class IBLT:
    def __init__(self, size, hash_count=3):
        self.size = size
        self.hash_count = hash_count
        self.table = [Cell() for _ in range(size)]

        # Mapa odwrotna do odzyskiwania stringów
        self.known_keys = {}     # key_int → key_str
        self.known_values = {}   # value_int → value_str

    #generowanie hash_count=3 roznych funkcji hashujacych do kodowania i dekodowania (uzycie roznych wartosci salt)
    def _hashes(self, key):
        hashes = []
        for i in range(self.hash_count):
            salted_key = f"{i}:{key}".encode('utf-8')
            h = int(hashlib.sha256(salted_key).hexdigest(), 16)
            hashes.append(h % self.size)
        return hashes

    #zmiana stringa na hash do uzycia XORa
    def _key_to_int(self, key):
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)

    #dodawanie pary (key, val) do IBLT
    def insert(self, key, value):
        #zamiana key i value na hashe
        key_int = self._key_to_int(key)
        value_int = self._key_to_int(value)

        #zapamietujemy nasze wartosci, to bedzie potrzebne do odzyskiwania orygnialnego key
        self.known_keys[key_int] = key
        self.known_values[value_int] = value

        #kodujemy nasze wartosci keys(source symbols), wrzucamy je do hash_count=3 cell
        for idx in self._hashes(key):
            cell = self.table[idx]
            cell.key_sum ^= key_int
            cell.value_sum ^= value_int
            cell.count += 1

    # usuwanie pary (key, val) z IBLT
    def delete(self, key, value):
        # poczatek taki sam jak w insert
        key_int = self._key_to_int(key)
        value_int = self._key_to_int(value)

        self.known_keys[key_int] = key
        self.known_values[value_int] = value

        #znowu XOR tak samo, bo jak chcemy usunac juz wartsoc ktora jest dodana XORem to wystarczy zrobic nia XORa jeszcze raz
        for idx in self._hashes(key):
            cell = self.table[idx]
            cell.key_sum ^= key_int
            cell.value_sum ^= value_int
            cell.count -= 1

    #dekodowanie kluczy i wartosci, ktorymi zbiory sie roznia
    def list_entries(self):
        entries = []
        deletions = []

        #changed pilnuje, czy coś nowego udało się właśnie odczytać
        changed = True
        while changed:
            changed = False
            for cell in self.table:
                #sprzwdzenie czy komorka zawiera tylko jedna wartosci (1: jesli nasz zbior ja posiada a ten drugi nie, -1 wpp)
                if abs(cell.count) == 1:
                    #odzyskujemy oryginalne stringi
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

                    # czyszczenie struktoru na koncu (chyba dla bezpieczenstwa i guess)
                    self.delete(key_str, value_str)
                    changed = True
                    break
        return entries, deletions

#tworzymy dwa zbiory A i B, A = {"a","b","c"}, B = {"b","c","d"}
iblt_A = IBLT(size=20)
iblt_A.insert("a", "val")
iblt_A.insert("b", "val")
iblt_A.insert("c", "val")

iblt_B = IBLT(size=20)
iblt_B.insert("b", "val")
iblt_B.insert("c", "val")
iblt_B.insert("d", "val")

# trzeba skopiowac wartosci tak, zeby oba zbiory wiedzialy jakie wartosci wgl istnieja
iblt_A.known_keys.update(iblt_B.known_keys)
iblt_A.known_values.update(iblt_B.known_values)

# odejmowanie B od A
for i in range(iblt_A.size):
    iblt_A.table[i].key_sum ^= iblt_B.table[i].key_sum
    iblt_A.table[i].value_sum ^= iblt_B.table[i].value_sum
    iblt_A.table[i].count -= iblt_B.table[i].count

# odczytanie roznic
inserted, deleted = iblt_A.list_entries()
print("Inserted:", inserted)
print("Deleted:", deleted)
