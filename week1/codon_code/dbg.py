from collections import defaultdict

class Node:
    def __init__(self):
        self.in_degree: int = 0
        self.out_degree: int = 0
        self.children: dict[int, int] = defaultdict(int)
        self.parents: dict[int, int] = defaultdict(int)

    def __str__(self) -> str:
        return f"in: {self.in_degree}, out: {self.out_degree}"

class DBG:
    def __init__(self):
        self.kmer_to_id: dict[str, int] = {}
        self.id_to_kmer: list[str] = []
        self.nodes: dict[int, Node] = {}
        self.kmer_count: int = 0

    def get_id(self, kmer: str) -> int:
        if kmer in self.kmer_to_id:
            return self.kmer_to_id[kmer]
        
        idx = self.kmer_count
        self.kmer_to_id[kmer] = idx
        self.id_to_kmer.append(kmer)
        self.nodes[idx] = Node()
        self.kmer_count += 1
        return idx