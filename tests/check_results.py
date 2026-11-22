"""Automatic checks for Module 4 project: Identify an unknown sequence.

Run from the top folder of your copy:   python tests/check_results.py
It reads only the files you commit in results/ and scripts/, uses the Python
standard library only, and prints PASS or FAIL for each task.
"""
import csv
import hashlib
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
_failed = []


class Fail(Exception):
    pass


def check(label):
    """Run one labelled check and print PASS or FAIL."""
    def wrap(fn):
        try:
            fn()
        except Fail as err:
            print(f"FAIL  {label}: {err}")
            _failed.append(label)
        except Exception as err:  # an unreadable file should guide, not crash
            print(f"FAIL  {label}: could not read your results ({type(err).__name__}: {err})")
            _failed.append(label)
        else:
            print(f"PASS  {label}")
        return fn
    return wrap


def finish():
    print()
    if _failed:
        print(f"{len(_failed)} check(s) failed. Read the messages above, fix that task and push again.")
        sys.exit(1)
    print("Every checkpoint passed. Well done.")


def need(path):
    path = Path(path)
    if not path.exists():
        raise Fail(f"{path.relative_to(ROOT)} not found; create it and commit it")
    return path


def read_rows(path):
    """Read a CSV (or tab-separated) file into a list of dicts with lower-case keys."""
    text = need(path).read_text(encoding="utf-8-sig")
    dialect = "excel-tab" if "\t" in text.splitlines()[0] else "excel"
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in rows]


def column(rows, *names, path=""):
    if not rows:
        raise Fail(f"{path} has no data rows")
    for n in names:
        if n in rows[0]:
            return n
    raise Fail(f"{path} needs a column called {names[0]}; found {', '.join(rows[0])}")


def num(value, what):
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        raise Fail(f"{what}: '{value}' is not a number")


def near(a, b, tol):
    return abs(a - b) <= tol


def _norm(text):
    return re.sub(r"\s+", " ", text.replace("\r", "")).strip()


def sha(path):
    return hashlib.sha256(_norm(Path(path).read_text(encoding="utf-8")).encode()).hexdigest()


def edited(path, starter_sha):
    path = need(path)
    if sha(path) == starter_sha:
        raise Fail(f"{path.relative_to(ROOT)} is still the untouched starter; write your code in it")
    return path


def png_info(path):
    """Width, height and dpi (None if not stored) of a PNG file."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", data[16:24])
    dpi = None
    i = 8
    while i + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[i:i + 8])
        if kind == b"pHYs":
            x, _, unit = struct.unpack(">IIB", data[i + 8:i + 17])
            if unit == 1:
                dpi = x * 0.0254
            break
        if kind == b"IDAT":
            break
        i += 12 + length
    return w, h, dpi


def image(path, min_px=300, min_bytes=5000):
    """Check that a PNG or SVG is a real image of sensible size; return PNG info."""
    path = need(path)
    rel = path.relative_to(ROOT)
    size = path.stat().st_size
    if size < min_bytes:
        raise Fail(f"{rel} is only {size} bytes; it looks empty")
    if path.suffix.lower() == ".svg":
        head = path.read_text(encoding="utf-8", errors="replace")[:5000]
        if "<svg" not in head:
            raise Fail(f"{rel} is not a valid SVG file")
        return None
    info = png_info(path)
    if info is None:
        raise Fail(f"{rel} is not a real PNG file (was it renamed from another format?)")
    w, h, _ = info
    if w < min_px or h < min_px // 3:
        raise Fail(f"{rel} is only {w} x {h} pixels; save it with a higher dpi")
    return info


def text_of(path, min_words=0):
    path = need(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    words = len(re.findall(r"\w+", text))
    if words < min_words:
        raise Fail(f"{path.relative_to(ROOT)} has {words} words; write at least {min_words}")
    return text


def read_fasta(path):
    recs, name, desc, seq = [], None, "", []
    for line in need(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(">"):
            if name is not None:
                recs.append((name, desc, "".join(seq)))
            parts = line[1:].split(None, 1)
            name, desc, seq = (parts[0] if parts else ""), (parts[1] if len(parts) > 1 else ""), []
        elif line:
            seq.append(line)
    if name is not None:
        recs.append((name, desc, "".join(seq)))
    return recs


UNKNOWN = read_fasta(DATA / "unknown.fa")[0][2]
REFS = {n: s for n, _, s in read_fasta(DATA / "references.fa")}
BETAS = ["HBB_HUMAN", "HBB1_MOUSE", "HBB_BOVIN", "HBB_HORSE", "HBB_CHICK"]


def region(n):
    """The 60 residues of reference n that match the unknown best (no gaps)."""
    ref = REFS[n]
    best = max(range(len(ref) - 59),
               key=lambda i: sum(a == b for a, b in zip(UNKNOWN, ref[i:i + 60])))
    return ref[best:best + 60]


def summary():
    rows = read_rows(RESULTS / "summary.tsv")
    column(rows, "key", path="results/summary.tsv")
    column(rows, "value", path="results/summary.tsv")
    return {r["key"]: r["value"] for r in rows}


def key(s, k):
    if k not in s or s[k] == "":
        raise Fail(f"results/summary.tsv has no value for '{k}'")
    return s[k]


@check("Setup · Your script")
def _():
    nb = list(SCRIPTS.glob("*.ipynb"))
    if nb:
        return              # a notebook in scripts/ is fine too
    edited(SCRIPTS / "identify_unknown.py", "a4612800ff5802a1c74716bf49f1b95583a70eb8b2a981d2b99b85282e32ec71")


# score, identity %, query cover %, gaps (from the lesson's checkpoint)
HITS = {"HBB_HUMAN": (318.0, 98.3, 100, 0), "HBB_HORSE": (270.0, None, None, None),
        "HBB1_MOUSE": (259.0, None, None, None), "HBB_BOVIN": (257.0, None, None, None),
        "HBB_CHICK": (229.0, None, None, None), "HBA_HUMAN": (143.0, 48.3, None, None),
        "MYG_HUMAN": (34.0, None, None, None), "LYSC_HUMAN": (21.0, 44.4, 30, 2)}


@check("Task 1 · Align and rank")
def _():
    path = "results/hits.tsv"
    rows = read_rows(RESULTS / "hits.tsv")
    for c in ("name", "score", "identity_pct", "query_cover_pct", "gaps"):
        column(rows, c, path=path)
    if len(rows) != 8:
        raise Fail(f"expected 8 rows in {path} (one per reference), found {len(rows)}")
    names = [r["name"] for r in rows]
    if sorted(names) != sorted(HITS):
        raise Fail(f"{path} should name each reference once, as in data/references.fa")
    scores = [num(r["score"], "score") for r in rows]
    if scores != sorted(scores, reverse=True):
        raise Fail(f"{path} is not sorted by score, highest first")
    for r in rows:
        score, ident, cover, gaps = HITS[r["name"]]
        if not near(num(r["score"], "score"), score, 0.6):
            raise Fail(f"the score for {r['name']} does not match the checkpoint; check the "
                       "aligner settings: local mode, BLOSUM62, gap opening -12, extension -1")
        if ident is not None and not near(num(r["identity_pct"], "identity_pct"), ident, 0.2):
            raise Fail(f"the percent identity for {r['name']} is off; divide identities by "
                       "identities + mismatches + gaps, and give it as a percentage")
        if cover is not None and not near(num(r["query_cover_pct"], "query_cover_pct"), cover, 1.5):
            raise Fail(f"the query cover for {r['name']} is off; use the span in the unknown "
                       "(aln.coordinates[0]) divided by 60, as a percentage")
        if gaps is not None and int(num(r["gaps"], "gaps")) != gaps:
            raise Fail(f"the number of gaps for {r['name']} is not right; read it from .counts()")


Z = {"HBB_HUMAN": (318.0, 25.5, 60.9), "HBA_HUMAN": (143.0, None, 21.6),
     "MYG_HUMAN": (34.0, None, 1.9), "LYSC_HUMAN": (21.0, 22.0, -0.3)}


@check("Task 2 · Check the scores against chance")
def _():
    path = "results/shuffle_scores.tsv"
    rows = read_rows(RESULTS / "shuffle_scores.tsv")
    for c in ("name", "real_score", "shuffled_mean", "shuffled_max", "z_score"):
        column(rows, c, path=path)
    got = {r["name"]: r for r in rows}
    missing = [n for n in Z if n not in got]
    if missing:
        raise Fail(f"{path} needs one row each for {', '.join(Z)}; missing {', '.join(missing)}")
    for n, (real, mean, z) in Z.items():
        r = got[n]
        if not near(num(r["real_score"], "real_score"), real, 0.6):
            raise Fail(f"the real score for {n} should match task 1")
        if mean is not None and not near(num(r["shuffled_mean"], "shuffled_mean"), mean, 0.3):
            raise Fail(f"the shuffled mean for {n} is off; did you call random.seed(1) once, "
                       "just before making the 200 shuffled copies?")
        if not near(num(r["z_score"], "z_score"), z, 0.3):
            raise Fail(f"the z-score for {n} is off; z = (real - mean) / standard deviation "
                       "of the shuffled scores (statistics.stdev)")
        if num(r["shuffled_max"], "shuffled_max") < num(r["shuffled_mean"], "shuffled_mean"):
            raise Fail(f"the shuffled maximum for {n} is below the mean")


@check("Task 3 · Multiple alignment and conservation")
def _():
    path = "results/beta_regions.fasta"
    recs = read_fasta(RESULTS / "beta_regions.fasta")
    names = [n for n, _, _ in recs]
    want = ["unknown"] + BETAS
    if sorted(names) != sorted(want):
        raise Fail(f"{path} should hold 6 sequences with the ids {', '.join(want)}; found "
                   f"{', '.join(names) or 'none'}")
    seqs = {n: s for n, _, s in recs}
    if seqs["unknown"] != UNKNOWN:
        raise Fail(f"the unknown in {path} is not the 60-residue fragment from data/unknown.fa")
    for n, desc, s in recs:
        if len(s) != 60:
            raise Fail(f"{n} in {path} has {len(s)} residues; cut exactly 60")
        if n != "unknown" and s not in REFS[n]:
            raise Fail(f"the region for {n} is not a stretch of its reference sequence")
    for n in BETAS:
        if seqs[n] != region(n):
            raise Fail(f"the region cut from {n} is shifted; start at the reference start minus "
                       "the start in the unknown (aln.coordinates)")
    conserved = sum(len({seqs[n][i] for n in want}) == 1 for i in range(60))
    s = summary()
    if int(num(key(s, "conserved_columns"), "conserved_columns")) != conserved:
        raise Fail("conserved_columns in results/summary.tsv does not match the columns of "
                   f"{path}; count columns where all six letters are the same")


def parse_newick(text):
    """Return the tree as nested lists of leaf names."""
    text = text.strip().rstrip(";")
    pos = 0

    def node():
        nonlocal pos
        if text[pos] == "(":
            pos += 1
            kids = [node()]
            while text[pos] == ",":
                pos += 1
                kids.append(node())
            pos += 1                      # ')'
            label = read_label()
            return kids
        return read_label()

    def read_label():
        nonlocal pos
        start = pos
        while pos < len(text) and text[pos] not in ",()":
            pos += 1
        return text[start:pos].split(":")[0].strip().strip("'")

    return node()


def leaves(t):
    return {t} if isinstance(t, str) else set().union(*(leaves(k) for k in t))


def clades(t, out):
    if isinstance(t, list):
        out.append(leaves(t))
        for k in t:
            clades(k, out)
    return out


@check("Task 4 · Build a tree")
def _():
    path = "results/distances.tsv"
    rows = read_rows(RESULTS / "distances.tsv")
    first = list(rows[0])[0] if rows else "name"
    table = {r[first]: r for r in rows}
    if "unknown" not in table:
        raise Fail(f"{path} needs a row called unknown")
    row = table["unknown"]
    d = {}
    for n in BETAS:
        k = n.lower()
        if k not in row:
            raise Fail(f"{path} needs a column for {n}")
        d[n] = num(row[k], f"distance unknown-{n}")
    nearest = min(d, key=d.get)
    if nearest != "HBB_HUMAN" or not near(d["HBB_HUMAN"], 1 / 60, 0.0006):
        raise Fail(f"the distances from the unknown in {path} do not match the checkpoint; "
                   "use DistanceCalculator('identity') on the task 3 alignment")
    if min(v for n, v in d.items() if n != "HBB_HUMAN") < 0.166:
        raise Fail(f"some distances in {path} are too small; check the alignment from task 3")
    tree = parse_newick(need(RESULTS / "tree.nwk").read_text(encoding="utf-8"))
    if leaves(tree) != {"unknown", *BETAS}:
        raise Fail("results/tree.nwk should have the six sequences of task 3 as its tips")
    if not isinstance(tree, list) or not any(k == "HBB_CHICK" for k in tree):
        raise Fail("in results/tree.nwk, HBB_CHICK should sit alone on one side of the root; "
                   "root the tree with chicken as the outgroup")
    if {"unknown", "HBB_HUMAN"} not in clades(tree, []):
        raise Fail("in results/tree.nwk the unknown does not pair with its nearest neighbour")
    s = summary()
    if key(s, "nearest_neighbour") != "HBB_HUMAN":
        raise Fail("nearest_neighbour in results/summary.tsv does not match your distance table")


@check("Task 5 · Describe the difference")
def _():
    s = summary()
    human = REFS["HBB_HUMAN"]
    diffs = [i for i, (a, b) in enumerate(zip(UNKNOWN, human[75:135]), start=1) if a != b]
    pos_u = diffs[0]
    if int(num(key(s, "position_in_unknown"), "position_in_unknown")) != pos_u:
        raise Fail("position_in_unknown is not right; walk along the unknown and the human "
                   "region together with zip, counting from 1")
    if int(num(key(s, "position_in_human"), "position_in_human")) != pos_u + 75:
        raise Fail("position_in_human is not right; count the first methionine of human HBB as 1")
    three = {"R": "arg", "K": "lys"}
    h, u = three[human[pos_u + 74]], three[UNKNOWN[pos_u - 1]]
    if key(s, "human_residue").lower() != h or key(s, "unknown_residue").lower() != u:
        raise Fail("human_residue and unknown_residue should be the three-letter codes of "
                   "the two residues at that position, for example Gly")
    hgvs = key(s, "hgvs").replace(" ", "").lower()
    if f"{h}{pos_u + 75}{u}" not in hgvs:
        raise Fail("hgvs should be written as in lesson 8: three-letter code, human position, "
                   "three-letter code, for example p.(Gly12Asp)")
    if key(s, "change_type").lower() != "missense":
        raise Fail("change_type is not right; one amino acid swapped for another is called?")
    if int(num(key(s, "blosum62_score"), "blosum62_score")) != 2:
        raise Fail("blosum62_score is not right; look the pair up with blosum62[a, b]")
    same = {x.strip().upper() for x in key(s, "species_with_lys").split(",") if x.strip()}
    want = {n for n in BETAS if region(n)[pos_u - 1] == UNKNOWN[pos_u - 1]}
    if same != want:
        raise Fail("species_with_lys does not match the column of your task 3 alignment; "
                   "list the reference names that share the unknown's residue")


@check("Task 6 · Write a short report")
def _():
    text = text_of(RESULTS / "report.md", min_words=120)
    low = text.lower()
    if "beta" not in low or not ("haemoglobin" in low or "hemoglobin" in low):
        raise Fail("results/report.md should name the protein family of the unknown")
    if "hbb_human" not in low and "human" not in low:
        raise Fail("results/report.md should name the closest reference")
    for label, pats in [("the identity of the top hit", [r"98\.3"]),
                        ("the z-scores from task 2", [r"60\.9|\b61\b", r"21\.6|1\.9"]),
                        ("the number of conserved columns", [r"\b35\b"])]:
        for p in pats:
            if not re.search(p, text):
                raise Fail(f"results/report.md should quote {label}, with your numbers")
    if "species" not in low:
        raise Fail("results/report.md should say what this reference set can and cannot tell "
                   "you about the species")


finish()
