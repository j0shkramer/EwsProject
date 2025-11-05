#!/usr/bin/env python3

import argparse, gzip

def get_args():
    parser = argparse.ArgumentParser(description="A program go through the peaks file and extract regions in the area of EwS-assoicated Genes")
    parser.add_argument("-f", "--file", help="Input peak file for the cell line")
    parser.add_argument("-o", "--output", help="Name of the output file for peaks in the regions of EwS-assoicated genes")
    parser.add_argument("-b", "--bedfile", help="BED File of assoicated genes")
    return parser.parse_args()

args = get_args()

# : dict[str, list]
ews_asc_genes = {}

# Open the bed file and put every gene's name, start, and stop position in a dictonary 
with open(args.bedfile, "r") as bed:
    for line in bed:
        curr_line = line.split('\t')
        chrom = curr_line[0]
        start = int(curr_line[1])
        end = int(curr_line[2])
        gene = curr_line[3]
        if chrom in ews_asc_genes:
            ews_asc_genes[chrom].append([start, end, gene])
        else:
            ews_asc_genes[chrom] = []
            ews_asc_genes[chrom].append([start, end, gene])

with open(args.output, "w") as output:
    with gzip.open(args.file, "rt") as peaks:
        for line in peaks:
            # Header line, want to remove starting "#"
            if line[0] == "#":
                line = line[1:]
                output.write(f'gene_name\t{line}')
            else:
                line = line.strip()
                curr_line = line.split()
                curr_chrom = curr_line[0]
                curr_peak_start = int(curr_line[1])
                curr_peak_end = int(curr_line[2])
                if curr_chrom in ews_asc_genes.keys():
                    gene_list = ews_asc_genes[curr_chrom]
                    for gene in gene_list:
                        curr_gene_start = gene[0]
                        curr_gene_end = gene[1]
                        curr_gene = gene[2].strip()
                        if curr_gene_start < curr_peak_end and curr_gene_end > curr_peak_start:
                            output.write(f'{curr_gene}\t{line}\n')
                else:
                    continue
                    

