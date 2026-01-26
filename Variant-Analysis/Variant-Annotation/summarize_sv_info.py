#!/usr/bin/env python3

import pandas as pd

sv_tab = pd.read_csv('ews_sv_genes.txt')
uniq_genes = set(sv_tab.gene.values)

cl_combo_dict = {}
for gene in uniq_genes:
    subset_sv_tab = sv_tab[sv_tab.gene == gene]
    cell_lines = sorted(list(set(subset_sv_tab.cell_line.values)))
    cell_line_combo = '-'.join(cell_lines)
    if cell_line_combo in cl_combo_dict:
        cl_combo_dict[cell_line_combo].append(gene)
    else:
        cl_combo_dict[cell_line_combo] = [gene]


combos = []
genes = []
for key in cl_combo_dict:
    for val in cl_combo_dict[key]:
        combos.append(key)
        genes.append(val)

export_df = pd.DataFrame()
export_df['CellLineCombo'] = combos
export_df['Gene'] = genes
export_df.to_csv("cell_line_combo_genes.csv", index = None)