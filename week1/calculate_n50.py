import sys

def fasta_contig_lengths(path):
    lengths, cur = [], 0
    try:
        with open(path, "r") as f:
            for line in f:
                if line.startswith(">"):
                    if cur: lengths.append(cur); cur = 0
                else:
                    cur += len(line.strip())
        if cur:
            lengths.append(cur)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        return []
    return lengths

def n50(lengths):
    if not lengths:
        return 0
    s = sorted(lengths, reverse=True)
    total = sum(s)
    acc = 0
    for L in s:
        acc += L
        if acc >= total / 2:
            return L
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_n50.py <contig.fasta>", file=sys.stderr)
        sys.exit(1)
    print(n50(fasta_contig_lengths(sys.argv[1])))
