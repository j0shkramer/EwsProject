#!/usr/bin/env python3

# import packages
import argparse
import pandas as pd
import numpy as np
import itertools
import re

# define command line arguments
def get_args():
    parser = argparse.ArgumentParser(description = 'A script to generate a simplified table of gene names/types, structural variant types/lengths, and cell line from an ANNOVAR output table.')
    parser.add_argument('-a', '--annovar', help = 'Tab separated .txt ANNOVAR output file', required = True, type = str)
    parser.add_argument('-o', '--output', help = 'Name of the output .csv file', required = True, type = str)
    parser.add_argument('-i', '--intergenic_split', action = 'store_true', help = 'Split intergenic variants into two lines (upstream and downstream genes)', required = False)
    return parser.parse_args()
args = get_args()

# read in ANNOVAR output table as a pandas dataframe + select useful columns
sv_table_annovar = pd.read_csv(args.annovar, sep = '\t')[['Func.ensGene', 'Gene.ensGene', 'Otherinfo11', 'CellLine']]
# rename columns for simplicity
sv_table_annovar.rename(columns = {'Func.ensGene': 'gene_type', 'Gene.ensGene': 'gene', 'CellLine':'cell_line'}, inplace = True)

# function for extracting type of structural variant: INS/DEL/DUP
def extract_sv_type(sv_info):
    return re.search(r'SVTYPE=(.{3});', sv_info).group(1)

# function for extracting structural variant length of insertions or duplications
def extract_sv_len_ins_dup(sv_info):
    return abs(int(re.search(r'SVLEN=(\d+)', sv_info).group(1)))

# function for extracting structural variant length of deletions (are listed as negative in vcf files)
def extract_sv_len_del(sv_info):
    return abs(int(re.search(r'SVLEN=(-\d+)', sv_info).group(1)))

# add structural variant type and length as new columns in dataframe
sv_table_annovar['sv_type'] = [extract_sv_type(info) for info in sv_table_annovar.Otherinfo11.values]
sv_table_annovar['sv_len'] = [extract_sv_len_del(sv_table_annovar.Otherinfo11.values[i]) if sv_table_annovar.sv_type.values[i] == "DEL" else extract_sv_len_ins_dup(sv_table_annovar.Otherinfo11.values[i]) for i in np.arange(len(sv_table_annovar.Otherinfo11.values))]
# delete info column
sv_table_annovar.drop('Otherinfo11', axis = 1, inplace = True)

# replace semicolons separating genes with commas
sv_table_annovar['gene'] = [gene_list.replace(';',',') for gene_list in sv_table_annovar.gene.values]

# split gene names into a list
sv_table_annovar['gene'] = [gene_list.split(',') for gene_list in sv_table_annovar.gene.values]
#sv_table_annovar['gene'] = [re.split(',|;', gene_list) for gene_list in sv_table_annovar.gene.values]

# remove duplicates
sv_table_annovar['gene'] = [list(set(gene_list)) for gene_list in sv_table_annovar.gene.values]


# remove gene names listed as 'NONE'
sv_table_annovar['gene'] = [[gene for gene in gene_list if gene != 'NONE'] for gene_list in sv_table_annovar.gene.values]

if args.intergenic_split:
    # making empty lists that will each turn into column in final dataframe
    gene_types = []
    genes = []
    cell_lines = []
    sv_types = []
    sv_lens = []

    # splitting up intergenic structural variants into multiple rows (one for each downstream/upstream gene)
    for ind, gene_list in enumerate(sv_table_annovar.gene.values):
        gene_type = sv_table_annovar.gene_type.values[ind]
        cell_line = sv_table_annovar.cell_line.values[ind]
        sv_type = sv_table_annovar.sv_type.values[ind]
        sv_len = sv_table_annovar.sv_len.values[ind]
        for gene in gene_list:
            genes.append(gene)
            gene_types.append(gene_type)
            cell_lines.append(cell_line)
            sv_types.append(sv_type)
            sv_lens.append(sv_len)

    # create final dataframe
    sv_output_table = pd.DataFrame()
    sv_output_table['gene_type'] = gene_types
    sv_output_table['gene'] = genes
    sv_output_table['cell_line'] = cell_lines
    sv_output_table['sv_type'] = sv_types
    sv_output_table['sv_len'] = sv_lens

else:
    # join genes into a single string
    sv_table_annovar['gene'] = ['|'.join(gene_list) for gene_list in sv_table_annovar.gene.values]
    sv_output_table = sv_table_annovar

# export resulting dataframe
sv_output_table.to_csv(args.output, index = False)


