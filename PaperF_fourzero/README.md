# Paper F: four-zero tail-palindromic primitive polynomial conjecture

Title: Four-zero tail-palindromic primitive polynomials: coefficient geometry, Dickson reduction, and computational evidence

Author: Baohua Li

Status: structural/computational draft.

Main content:
- self-paired even target \(H_{\mathrm{even}}=Q_k\oplus V_k\);
- insertion-poset/Pascal description of four-zero candidates;
- exact symmetric-weight gcd formula with \(2^n-1\);
- exact multiplicity distribution, explicit Fourier spectrum, closed-form second moment, and all-moment formulas for the four-zero \(K\)-coset multiplicity;
- uniform Dickson/\(\tau\)-reduction for every even degree \(n=2k\), specializing to the \(n=2p\) analysis;
- self-reciprocal bridge via \(x f(x)+1\);
- \(K\)-coset count for four-zero candidates;
- half-space functional \(s\);
- \(n=2p\) necessary Dickson-factor filter \(\mathcal S_p(T)\);
- exact computational data up to \(n=200\) and first solutions to \(n=300\);
- negative finite-pair association conjecture for \(n=2p\), supported by \(p\le97\);
- analytic barrier to single-candidate Weil estimates.

Files:
- `PaperF_fourzero.tex` - main manuscript;
- `PaperF_fourzero.pdf` - compiled PDF (14 pages).

Compile:
```bash
pdflatex PaperF_fourzero.tex
pdflatex PaperF_fourzero.tex
```

Reproducibility:
- `_analyze_zero_pairs.py`
- `_find_palindromic_primitive.py`
- `_fourzero_n4_two_lines.py`
- `_fourzero_pair_association.py`
- `_extend_fourzero_first_202_250.py`
- `_extend_fourzero_first_252_300.py`
- `_四零回文本原计数_6到200.json`
- `_四零回文本原_数量分布_6到200.md`
- `_四零回文_2p_有限配对关联.json`
- `_四零回文_2p_有限配对关联.md`
- `_factordb_2n_minus_1_cache.json`
- `_四零首解_202到250.json`
- `_四零首解_252到300.json`
- `_fourzero_factors_6_300.txt`

General companion repository for related preprints:
https://github.com/63183349121/yijing-mathematical-structures

Paper F assets are available from the author and in this directory.

Suggested arXiv classification:
- Primary: math.NT
- Cross-list: math.CO, math.AC
- MSC: 11T06, 11T30, 12E20, 68W30
