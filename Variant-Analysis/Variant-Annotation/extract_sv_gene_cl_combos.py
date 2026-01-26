#!/usr/bin/env python3

# import packages
import argparse
import pandas as pd

# define command line arguments
def get_args():
    parser = argparse.ArgumentParser(description = 'A script to generate a table specifying the combination of cell lines having structural variants in/near each gene.')
    parser.add_argument('-i', '--input', help = 'Comma separated file containing gene, cell_line, and gene_type columns', required = True, type = str)
    parser.add_argument('-o', '--output', help = 'Name of output .csv file', required = True, type = str)
    return parser.parse_args()
args = get_args()

# read in input table
sv_tab = pd.read_csv(args.input)
uniq_genes = set(sv_tab.gene.values)


# create dictionary:
## key = combination of cell lines separated by a "-" delimiter (str)
## value = list of genes that have structural variants in the key cell lines
cl_combo_dict = {}

for gene in uniq_genes:
    subset_sv_tab = sv_tab[sv_tab.gene == gene]
    # get list of cell lines, sorted in alphabetical order, that have a variant associated with that gene
    cell_lines = sorted(list(set(subset_sv_tab.cell_line.values)))
    # join cell lines into a single string
    cell_line_combo = '-'.join(cell_lines)

    # update dictionary
    if cell_line_combo in cl_combo_dict:
        cl_combo_dict[cell_line_combo].append(gene)
    else:
        # start a key-value pair for cell line combination if it is not in the dictionary already
        cl_combo_dict[cell_line_combo] = [gene]


combos = []
genes = []
# create columns for table to export (1 row for each gene)
for key in cl_combo_dict:
    for val in cl_combo_dict[key]:
        combos.append(key)
        genes.append(val)

# put columns into a Pandas dataframe
export_df = pd.DataFrame()
export_df['CellLineCombo'] = combos
export_df['Gene'] = genes

# export dataframe
export_df.to_csv(args.output, index = False)