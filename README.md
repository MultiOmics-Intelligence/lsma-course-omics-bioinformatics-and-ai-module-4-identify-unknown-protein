<a href="https://lsma.co.uk/courses"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/lsma-walk-courses.svg" alt="LSMA, London School of Multiomics and AI: learn by doing, on real data" width="100%"></a>

# Module 4 project: Identify an unknown sequence

LSMA · Omics, Bioinformatics and AI · Module 4 project

<p>
<img src="https://img.shields.io/badge/LSMA-free%20course-D9481F?style=flat-square" alt="LSMA free course">
<img src="https://img.shields.io/badge/course-Omics%2C%20Bioinformatics%20and%20AI-0F1B33?style=flat-square" alt="Course">
<img src="https://img.shields.io/badge/language-Bash%20%7C%20Python-4EAA25?style=flat-square&logo=gnubash&logoColor=white" alt="Language">
<img src="https://img.shields.io/badge/checks-automatic-2F7D5B?style=flat-square&logo=githubactions&logoColor=white" alt="Automatic checks">
</p>

## Research question

A colleague sends you a 60-residue protein fragment with no label. What protein is it, which species could it come from, and how does it differ from its closest known relative?

## What you will build

| Files in (`data/`) | Files out (`results/`) |
|---|---|
| `unknown.fa`, the 60-residue fragment | `hits.tsv`, the eight hits, ranked by score |
| `references.fa`, eight real proteins from UniProt | `shuffle_scores.tsv`, real scores against 200 shuffled copies |
| | `beta_regions.fasta`, the six 60-residue regions, stacked |
| | `distances.tsv` and `tree.nwk`, the distance table and the tree |
| | `summary.tsv`, the numbers from tasks 3 to 5 |
| | `report.md`, your short report |

Your code lives in `scripts/identify_unknown.py`, task by task. The column names for each file are given in the TODO comments.

## Before you start

1. Get your own copy. Use the GitHub Classroom invitation link in the project lesson on [lsma.co.uk](https://lsma.co.uk), or press **Use this template** on this page.
2. Clone your copy to your computer, or open it in GitHub Codespaces.
3. Install the package once: `pip install biopython`.
4. Work in `scripts/`. Run everything from the top folder of your copy: `python scripts/identify_unknown.py`. You can explore in a Colab notebook first, as the lesson does; the script is what you hand in. (A notebook saved in `scripts/` is accepted too.)
5. Write every output to `results/`, with the exact file names above.

Use the same settings throughout. One aligner, set up once in task 1, is reused in every task: local mode, BLOSUM62, gap opening −12 and gap extension −1. If you change a setting, every score changes, and the checkpoints will no longer match. Fix the random seed in task 2 with `random.seed(1)`.

You can run the checks yourself at any time: `python tests/check_results.py`.

## Tasks

### 1. Align and rank

Lesson to revisit: Module 4, lessons 3 and 5.

Set up a local `PairwiseAligner` with BLOSUM62, gap opening −12 and extension −1. Align the unknown to each of the eight references. For each, record the score, the percent identity, the query cover and the number of gaps, and sort the hits by score. Save `results/hits.tsv`.

**Checkpoint:** HBB_HUMAN is the top hit, score 318.0, 98.3% identity over 100% of the unknown, no gaps. Then HBB_HORSE 270.0, HBB1_MOUSE 259.0, HBB_BOVIN 257.0, HBB_CHICK 229.0, HBA_HUMAN 143.0 (48.3%), MYG_HUMAN 34.0 and LYSC_HUMAN 21.0. Lysozyme shows 44.4% identity, but over only 30% of the unknown and with 2 gaps.

### 2. Check the scores against chance

Lesson to revisit: Module 4, lessons 4 and 5.

Make 200 shuffled copies of the unknown, with `random.seed(1)`. For HBB_HUMAN, HBA_HUMAN, MYG_HUMAN and LYSC_HUMAN, compare the real score with the scores of the shuffled copies, and compute a z-score. Save `results/shuffle_scores.tsv`.

**Checkpoint:** HBB_HUMAN: real 318.0, shuffled mean 25.5, shuffled maximum 48.0, z = 60.9. HBA_HUMAN: z = 21.6. MYG_HUMAN: z = 1.9. LYSC_HUMAN: real 21.0, shuffled mean 22.0, z = −0.3, no better than chance.

### 3. Multiple alignment and conservation

Lesson to revisit: Module 4, lesson 6.

For each of the five beta globins, cut out the 60-residue region that matches the unknown, and stack the six sequences into a `MultipleSeqAlignment`. Mark the fully conserved columns and count them. Save the six sequences as `results/beta_regions.fasta`.

**Checkpoint:** the regions are residues 76–135 of human, mouse and chicken, 74–133 of cow and 75–134 of horse. 35 of the 60 columns are fully conserved.

### 4. Build a tree

Lesson to revisit: Module 4, lesson 7.

Compute identity distances from the alignment of task 3 and build a neighbour-joining tree. Root it with chicken as the outgroup, draw it, and say where the unknown sits. Save `results/distances.tsv` and `results/tree.nwk`.

**Checkpoint:** the unknown pairs with HBB_HUMAN, at a distance of 0.016667, which is 1 difference in 60. Every other distance from the unknown is 0.166667 or more. Chicken sits alone on one side of the root.

### 5. Describe the difference

Lesson to revisit: Module 4, lessons 4, 6 and 8.

Find the one position where the unknown differs from HBB_HUMAN, and give it in human numbering, counting the first methionine as 1. Write the change in HGVS protein style, say what type of change it is, and look at the same column in the other species. Save the numbers of tasks 3 to 5 in `results/summary.tsv`.

**Checkpoint:** position 30 of the unknown, which is position 105 of human HBB: Arg in human, Lys in the unknown. A missense change, Arg105Lys. Cow also has Lys there; mouse, horse and chicken have Arg. BLOSUM62 scores the swap +2.

### 6. Write a short report

Lesson to revisit: Module 4, lessons 1–8.

In `results/report.md`, answer the research question in two or three sentences, then give the evidence from tasks 1–5 in one sentence each. State the limits of what this small search can show.

**Checkpoint:** your report names the protein family and the closest reference, quotes identity, z-scores, conservation and the tree with your numbers, and says that the species cannot be pinned down from this reference set alone.

## Hand in

Commit and push `scripts/` and `results/`. The **Checks** tab (GitHub Actions) then runs. A green tick means every checkpoint passed. You can push as often as you like.

## If a check fails

Open the failed run in the Actions tab and read the log. Each line starts with PASS or FAIL and names the task, for example `FAIL  Task 2 · Check the scores against chance: ...`. The message tells you what to look at, not the answer. Fix that task, run your script again and push.

## Getting help

- The project lesson on lsma.co.uk, and the earlier lessons named in each task.
- Helix, the course tutor.
- Email info@lsma.co.uk.

Never post personal data in public, in an issue, a commit or a file.

**Follow LSMA**

<p>
  <a href="https://lsma.co.uk"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-website.svg" alt="LSMA: lsma.co.uk" height="54"></a>
  <a href="https://www.linkedin.com/showcase/113252126/"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-linkedin.svg" alt="LSMA on LinkedIn" height="54"></a>
  <a href="https://www.instagram.com/lsma.uk/"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-instagram.svg" alt="LSMA on Instagram: @lsma.uk" height="54"></a>
  <a href="mailto:info@lsma.co.uk"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-email.svg" alt="Email: info@lsma.co.uk" height="54"></a>
</p>

Good luck, and enjoy the project.

**Dr. Anas Alzaeem**<br>
Academic Director, LSMA

[![Dr. Anas Alzaeem, Academic Director, LSMA](https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/signature/LSMA_Banner_Anas_Alzaeem.png)](https://lsma.co.uk)

© 2026 MultiOmics Intelligence Ltd. LSMA is the education arm of MultiOmics Intelligence. Code licensed under MIT.
