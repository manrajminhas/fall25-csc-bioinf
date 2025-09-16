class Node:
    def __init__(self):
        self.in_degree = 0
        self.out_degree = 0
        self.children = {}
        self.parents = {}

    def __str__(self):
        return "in: " + str(self.in_degree) + ", out: " + str(self.out_degree)

class DBG:
    def __init__(self):
        self.kmer_to_id = {}
        self.id_to_kmer = []
        self.nodes = {}
        self.kmer_count = 0

    def get_id(self, kmer):
        if kmer in self.kmer_to_id:
            return self.kmer_to_id[kmer]
        idx = self.kmer_count
        self.kmer_to_id[kmer] = idx
        self.id_to_kmer.append(kmer)
        self.nodes[idx] = Node()
        self.kmer_count += 1
        return idx
