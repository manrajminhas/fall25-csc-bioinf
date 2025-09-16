import sys
from utils import get_reads, get_reverse_complement
from dbg import DBG

k = 25
max_contigs = 20

def build_dbg(reads, dbg):
    for read in reads:
        if len(read) < k:
            continue
        for i in range(len(read) - k + 1):
            k1 = read[i:i+k]
            if i + k < len(read):
                k2 = read[i+1:i+1+k]
                id1 = dbg.get_id(k1)
                id2 = dbg.get_id(k2)
                if id2 not in dbg.nodes[id1].children:
                    dbg.nodes[id1].out_degree += 1
                    dbg.nodes[id2].in_degree += 1
                dbg.nodes[id1].children[id2] = dbg.nodes[id1].children.get(id2, 0) + 1
                dbg.nodes[id2].parents[id1] = dbg.nodes[id2].parents.get(id1, 0) + 1
        rc = get_reverse_complement(read)
        for i in range(len(rc) - k + 1):
            k1 = rc[i:i+k]
            if i + k < len(rc):
                k2 = rc[i+1:i+1+k]
                id1 = dbg.get_id(k1)
                id2 = dbg.get_id(k2)
                if id2 not in dbg.nodes[id1].children:
                    dbg.nodes[id1].out_degree += 1
                    dbg.nodes[id2].in_degree += 1
                dbg.nodes[id1].children[id2] = dbg.nodes[id1].children.get(id2, 0) + 1
                dbg.nodes[id2].parents[id1] = dbg.nodes[id2].parents.get(id1, 0) + 1

def get_depth(v_id, visited, depths, max_child, dbg):
    if visited.get(v_id, False):
        return depths[v_id]
    visited[v_id] = True
    max_d = 0
    max_c = -1
    for c_id, count in sorted(dbg.nodes[v_id].children.items(), key=lambda kv: kv[1], reverse=True):
        d = get_depth(c_id, visited, depths, max_child, dbg)
        if d > max_d:
            max_d = d
            max_c = c_id
    depths[v_id] = max_d + 1
    max_child[v_id] = max_c
    return depths[v_id]

def get_longest_path(dbg):
    visited = {}
    depths = {}
    max_child = {}
    max_d = 0
    max_v = -1
    for v in dbg.nodes:
        if not visited.get(v, False):
            d = get_depth(v, visited, depths, max_child, dbg)
            if d > max_d:
                max_d = d
                max_v = v
    path = []
    cur = max_v
    while cur != -1:
        path.append(cur)
        cur = max_child.get(cur, -1)
    return path

def delete_path(dbg, path):
    for v in path:
        if v in dbg.nodes:
            for p in list(dbg.nodes[v].parents.keys()):
                if p in dbg.nodes and v in dbg.nodes[p].children:
                    del dbg.nodes[p].children[v]
            for c in list(dbg.nodes[v].children.keys()):
                if c in dbg.nodes and v in dbg.nodes[c].parents:
                    del dbg.nodes[c].parents[v]
            del dbg.nodes[v]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: codon run -release codon_code/main.py <data_dir>")
        sys.exit(1)
    data_dir = sys.argv[1]
    reads = get_reads(data_dir)
    dbg = DBG()
    build_dbg(reads, dbg)
    out_fa = data_dir + ("" if data_dir.endswith("/") else "/") + "contig.fasta"
    with open(out_fa, "w") as f:
        for i in range(max_contigs):
            path = get_longest_path(dbg)
            if not path or len(path) < k:
                break
            contig = dbg.id_to_kmer[path[0]]
            for j in range(1, len(path)):
                contig += dbg.id_to_kmer[path[j]][-1]
            f.write(">contig_" + str(i+1) + "\n" + contig + "\n")
            delete_path(dbg, path)
