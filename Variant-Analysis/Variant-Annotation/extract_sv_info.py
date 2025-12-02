#!/usr/bin/env python3

# import packages
import argparse
import pandas as pd
import numpy as np
import itertools
import re

# define command line arguments
def get_args():
    parser = argparse.ArgumentParser(description = 'A script to generate a simplified table of gene names/types, structural variant types/lengths, and cell line from an ANNOVAR output table')
    parser.add_argument('-a', '--annovar', help = 'Tab separated .txt ANNOVAR output file', required = True, type = str)
    parser.add_argument('-o', '--output', help = 'Name of the output .csv file', required = True, type = str)
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

# split gene names into a list
sv_table_annovar['gene'] = [gene_list.split(',') for gene_list in sv_table_annovar.gene.values]
# remove gene names listed as 'NONE'
sv_table_annovar['gene'] = [[gene for gene in gene_list if gene != 'NONE'] for gene_list in sv_table_annovar.gene.values]

# function for splitting up a pandas series of lists
## source: https://stackoverflow.com/questions/40569402/pandas-create-several-rows-from-column-that-is-a-list
## posted by piRSquared
def melt_series(s):
    '''
    Input: pandas series of lists
    Output: pandas series that has broken up lists into individual elements with original indices retained
    '''
    lengths = s.str.len().values
    flat = [i for i in itertools.chain.from_iterable(s.values.tolist())]
    idx = np.repeat(s.index.values, lengths)
    return pd.Series(flat, idx, name = s.name)

# each gene in a list of genes gets split into its own row w/ all other values duplicated
sv_output_table = melt_series(sv_table_annovar.gene).to_frame().join(sv_table_annovar.drop('gene', axis = 1)).reset_index(drop = True)

# export resulting dataframe
sv_output_table.to_csv(args.output, index = False)