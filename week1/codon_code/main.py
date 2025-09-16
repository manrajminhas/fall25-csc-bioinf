import sys
from utils import get_reads, get_reverse_complement
from dbg import DBG



k: int = 25
max_contigs: int = 20

def build_dbg(reads: list[str], dbg: DBG):
    for read in reads:
        if len(read) < k:
            continue
        # Forward strand
        for i in range(len(read) - k + 1):
            kmer1 = read[i:i + k]
            if i + k < len(read):
                kmer2 = read[i + 1:i + 1 + k]
                id1 = dbg.get_id(kmer1)
                id2 = dbg.get_id(kmer2)
                if id2 not in dbg.nodes[id1].children:
                    dbg.nodes[id1].out_degree += 1
                    dbg.nodes[id2].in_degree += 1
                    dbg.nodes[id1].children[id2] = 0
                    dbg.nodes[id2].parents[id1] = 0
                dbg.nodes[id1].children[id2] += 1
                dbg.nodes[id2].parents[id1] += 1
        
        # Reverse complement strand
        rc_read = get_reverse_complement(read)
        for i in range(len(rc_read) - k + 1):
            kmer1 = rc_read[i:i + k]
            if i + k < len(rc_read):
                kmer2 = rc_read[i + 1:i + 1 + k]
                id1 = dbg.get_id(kmer1)
                id2 = dbg.get_id(kmer2)
                if id2 not in dbg.nodes[id1].children:
                    dbg.nodes[id1].out_degree += 1
                    dbg.nodes[id2].in_degree += 1
                    dbg.nodes[id1].children[id2] = 0
                    dbg.nodes[id2].parents[id1] = 0
                dbg.nodes[id1].children[id2] += 1
                dbg.nodes[id2].parents[id1] += 1

def get_depth(v_id: int, visited: dict[int, bool], depths: dict[int, int], max_child: dict[int, int], dbg: DBG) -> int:
    if v_id in visited and visited[v_id]:
        return depths[v_id]
    
    visited[v_id] = True
    max_d: int = 0
    max_c: int = -1

    sorted_children = sorted(dbg.nodes[v_id].children.items(), key=lambda item: item[1], reverse=True)
    
    for c_id, count in sorted_children:
        depth = get_depth(c_id, visited, depths, max_child, dbg)
        if depth > max_d:
            max_d = depth
            max_c = c_id

    depths[v_id] = max_d + 1
    max_child[v_id] = max_c
    return depths[v_id]

def get_longest_path(dbg: DBG) -> list[int]:
    visited: dict[int, bool] = {}
    depths: dict[int, int] = {}
    max_child: dict[int, int] = {}

    max_d: int = 0
    max_v_id: int = -1

    for v_id in dbg.nodes:
        if v_id not in visited or not visited[v_id]:
            d = get_depth(v_id, visited, depths, max_child, dbg)
            if d > max_d:
                max_d = d
                max_v_id = v_id
    
    path: list[int] = []
    curr_v_id = max_v_id
    while curr_v_id != -1:
        path.append(curr_v_id)
        curr_v_id = max_child.get(curr_v_id, -1)
        
    return path

def delete_path(dbg: DBG, path: list[int]):
    for v_id in path:
        if v_id in dbg.nodes:
            for p_id in list(dbg.nodes[v_id].parents.keys()):
                if p_id in dbg.nodes and v_id in dbg.nodes[p_id].children:
                    del dbg.nodes[p_id].children[v_id]
            for c_id in list(dbg.nodes[v_id].children.keys()):
                 if c_id in dbg.nodes and v_id in dbg.nodes[c_id].parents:
                    del dbg.nodes[c_id].parents[v_id]
            del dbg.nodes[v_id]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: codon run -release codon_code/main.py <data_dir>")
        sys.exit(1)

    data_dir = sys.argv[1]
    reads = get_reads(data_dir)
    dbg = DBG()
    build_dbg(reads, dbg)

    # Fixed output path to be 'contigs.fasta' in the current directory
    with open('contigs.fasta', 'w') as f:
        for i in range(max_contigs):
            path = get_longest_path(dbg)
            if not path or len(path) < k:
                break
            
            contig = dbg.id_to_kmer[path[0]]
            for j in range(1, len(path)):
                contig += dbg.id_to_kmer[path[j]][-1]
            
            f.write(f'>contig_{i+1}\n')
            f.write(contig + '\n')
            
            delete_path(dbg, path)