# Data

| File | What it is | Source and licence |
|---|---|---|
| `unknown.fa` | The 60-residue protein fragment with no label, as in the lesson's data block. | A real UniProtKB/Swiss-Prot sequence; which one is given only in the lesson's model answer. |
| `references.fa` | The eight reference proteins of the lesson: haemoglobin beta from human (P68871), mouse (P02088), cow (P02070), horse (P02062) and chicken (P02112), human haemoglobin alpha (P69905), human myoglobin (P02144) and human lysozyme (P61626). The accession is the second word of each header. | UniProtKB/Swiss-Prot, [www.uniprot.org](https://www.uniprot.org). Sequences checked against UniProt release 2026_04 on 22 November 2026. UniProt data are available under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) licence. |

Both files are copied exactly from the lesson. No synthetic data are used in this project.

To refresh a sequence from UniProt yourself, for example human haemoglobin beta:

```bash
curl -s https://rest.uniprot.org/uniprotkb/P68871.fasta
```

Cite: The UniProt Consortium (2025), UniProt: the Universal Protein Knowledgebase in 2025, Nucleic Acids Research 53: D609-D617.
