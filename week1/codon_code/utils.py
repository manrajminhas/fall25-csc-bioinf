import os

def get_reads(dir):
    reads = []
    for name in ("short_1.fasta", "short_2.fasta"):
        # Use string concatenation instead of os.path.join
        path = dir + "/" + name
        with open(path, "r") as f:
            for line in f:
                if not line.startswith(">"):
                    reads.append(line.strip())
    
    # Use string concatenation instead of os.path.join
    path = dir + "/" + "long.fasta"
    print(path)
    with open(path, "r") as f:
        for line in f:
            if not line.startswith(">"):
                reads.append(line.strip())
    return reads

_RC = {
    'A':'T','T':'A','C':'G','G':'C',
    'a':'t','t':'a','c':'g','g':'c',
    'N':'N','n':'n'
}

def get_reverse_complement(read):
    out = []
    i = len(read) - 1
    while i >= 0:
        ch = read[i]
        out.append(_RC[ch] if ch in _RC else ch)
        i -= 1
    return "".join(out)