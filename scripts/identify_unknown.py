"""Module 4 project: identify an unknown sequence.

Run from the top folder of your copy:   python scripts/identify_unknown.py
You can also work in a Colab notebook first (the lesson does), but keep this
script as the final, rerunnable version. Every result goes into results/.

Install once:   pip install biopython
"""
from pathlib import Path

from Bio import SeqIO

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# The unknown and the reference set (the same data block as in the lesson)
unknown = str(next(SeqIO.parse(DATA / "unknown.fa", "fasta")).seq)
refs = {r.id: str(r.seq) for r in SeqIO.parse(DATA / "references.fa", "fasta")}
print("Unknown:", len(unknown), "residues")
for name, seq in refs.items():
    print(f"{name:11}", len(seq))

# Research question (write it in your own words):
# TODO

# ---------------------------------------------------------------------------
# Task 1 · Align and rank (lessons 3 and 5)
# ---------------------------------------------------------------------------
# TODO: set up ONE local PairwiseAligner: BLOSUM62, gap opening -12, extension -1.
#       Reuse it in every task.
# TODO: align the unknown to each of the eight references; take aligner.align(unknown, seq)[0].
# TODO: for each hit, record score, percent identity (identities / (identities +
#       mismatches + gaps) x 100), query cover (span in the unknown / 60 x 100) and gaps.
# TODO: sort by score, highest first, and save results/hits.tsv (tab-separated) with
#       the columns: name, accession, score, identity_pct, query_cover_pct, gaps
#       (the accession is the second word of each FASTA header in data/references.fa).

# ---------------------------------------------------------------------------
# Task 2 · Check the scores against chance (lessons 4 and 5)
# ---------------------------------------------------------------------------
# TODO: random.seed(1), then make 200 shuffled copies of the unknown.
# TODO: for HBB_HUMAN, HBA_HUMAN, MYG_HUMAN and LYSC_HUMAN, score the real unknown and
#       every shuffled copy with aligner.score(a, b); compute the z-score.
# TODO: save results/shuffle_scores.tsv with the columns:
#       name, real_score, shuffled_mean, shuffled_max, z_score

# ---------------------------------------------------------------------------
# Task 3 · Multiple alignment and conservation (lesson 6)
# ---------------------------------------------------------------------------
# TODO: for each of the five beta globins, cut out the 60-residue region that matches
#       the unknown (start in reference minus start in unknown, then 60 residues).
# TODO: stack the unknown and the five regions into a MultipleSeqAlignment.
# TODO: mark and count the fully conserved columns.
# TODO: save the six sequences as results/beta_regions.fasta, ids: unknown, HBB_HUMAN,
#       HBB1_MOUSE, HBB_BOVIN, HBB_HORSE, HBB_CHICK. Put the region (for example 76-135)
#       after the id in each header.

# ---------------------------------------------------------------------------
# Task 4 · Build a tree (lesson 7)
# ---------------------------------------------------------------------------
# TODO: identity distances from the task 3 alignment; neighbour-joining tree.
# TODO: root it with HBB_CHICK as the outgroup, share the root branch, draw it.
# TODO: save results/distances.tsv (a square table: first column name, then one
#       column per sequence) and the tree as results/tree.nwk (Phylo.write, "newick").

# ---------------------------------------------------------------------------
# Task 5 · Describe the difference (lessons 4, 6 and 8)
# ---------------------------------------------------------------------------
# TODO: find the one position where the unknown differs from HBB_HUMAN; give it in the
#       unknown and in human numbering (first methionine = 1).
# TODO: write it in HGVS protein style with three-letter codes, say what type of change
#       it is, read the same column in the other species, look the pair up in BLOSUM62.

# ---------------------------------------------------------------------------
# Save the numbers from tasks 3 to 5 in results/summary.tsv
# ---------------------------------------------------------------------------
# Two columns, key and value, one row per key:
#   conserved_columns, nearest_neighbour, nearest_distance,
#   position_in_unknown, position_in_human, human_residue, unknown_residue,
#   hgvs, change_type, blosum62_score, species_with_lys
# (species_with_lys: the reference names that share the unknown's residue, comma-separated)

# ---------------------------------------------------------------------------
# Task 6 · Write a short report (lessons 1-8)
# ---------------------------------------------------------------------------
# Write results/report.md by hand (not from this script): answer the research
# question in two or three sentences, then one sentence of evidence per task, then
# the limits of what this small search can show.
