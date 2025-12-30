# Saturday, October 18th

/projects/bgmp/shared/groups/2025/sarcoma

## Exploratory Data Analysis

Cell lines are stored in /shared
- A673, A4573, CHLA9, CHLA10, PDX305, RDES, SKNMC, TC32, TC71

### FiberTools
https://fiberseq.github.io/fire/outputs.html 

FIRE: Mtase sensitive patches (MSPs) that are inferred to be regulatory elements on single chromatin fibers

Outputs
- filtered.cram
    - CRAM file that contians all the data used in the FIRE pipeline
    - Can be viewed with IGV or other genome browsers

- peaks.bed.gz
    - Chrom: Chromosome peak is located on
    - peak*start: Start of peak
    - peah_end: End of peak
    - start: start of the maximum of the peka
    - end: end of the maximum of the peak
    - coverage: coverage of the peak
    - fire_coverage: coverage of the FIREs in the peak
    - fire_coverage: Coverage of the FIREs in the peak
    - score: FIRE score of the peak
    - nuc_coverage: Coverage of the nucleosomes in the peak
    - msp_coverage: Coverafge of the MSPs in the peak
    - .**{H1,H2}: Repeats of the nuc_coverage and msp_coverage but for the two haplotypes
    - FDR: False discovery rate of the peak

- {sample}-fire-{v}-hap.differences.bed.gz
    - Same as the previous file, but includes a p_value and p_adjust column that shows the difference in coverage between the two haplotypes

- {sample}-fire-{v}-pileup.bed.gz
    - BED file containing per-base information on the number of FIREs, MSPs, nucleosomes, coverage and more

- {sample}-fire-{v}-qc.tbl.gz
    - Contains quality control metrics for the FIRE CRAM

### HLA

HLA Genes
- Encode cell-surface proteins that help the immune system between the self and non-self
- Present antigens to T cells, triggering immune response

Outputs
- {sample}-fifihla_asm.contigs.h1.fasta.fai
    - Index file for the FASTQ
- {sample}-fifihla_asm.contigs.h1.fasta
    - Contains only the targeted HLA loci extracted from the full contigs
- {sample}-hifihla_report.tsv
    - Summary of HLA allele calls per locus
- {sample}-hifihla_report.json
    -  Detailed allele call information, including alignment stats, coverage, and differences

### PacBio WGS WDL

https://github.com/PacificBiosciences/HiFi-human-WGS-WDL

Outputs
- {sample}.length.nonref.counts.tsv
    - Counts of non-reference alleles at tandem repeat loci
- {sample}.length.nonref.tsv
    - More detailed version of above
    - Repeat locus coordinates, obsereved allele lengths, read support per allele
- {sample}.length.vcf.gz
    - Contains tandem repeat genotyping results
    - Genomic positions of tandem reapts. genotyped alleles, quality scores and annotations
- {sample}-spanning.bam
    - BAM file containing reads tha span tandem repeat regions
    - Enables visualization of repeat regions in genome browsers

### pacbiowdlR

https://scfurl.github.io/pacbiowdlR/index.html 

- Offers a suite of functions for visualizing and downstream processing of PacBio WGS WDL workflows

# Sunday, October 19th

## Exploring 9cl_seurat.rds with Seurat and Signac

https://zenodo.org/records/12209095 

https://stuartlab.org/signac/

https://satijalab.org/seurat/ 

{name} = readRDS("path_to_9cl_seurat.rds)

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca

Everything came from one cell line titled: EW?

library(VariantAnnotation)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)
library(biomaRt)

mart <- useMart("ensembl", dataset = "hsapiens_gene_ensembl")

bed_data <- getBM(
  attributes = c("external_gene_name", "chromosome_name", "start_position", "end_position"),
  filters = "external_gene_name",
  values = gene_list,
  mart = mart
)

# Wednesday, October 22th

## Creating a BED file of EwS Assiocated Genes

Used the R library readxl to convert the Excel file of EwS assiocated genes found through literature into R, then extracted the external gene name, chromosome name, start and end position for each EwS assiocated gene

There was an issue with some of the genes not being listed on canonical chromosomes, I had to remove these genes from the data set because they would have issues with future analysis down the line. 

The BED file was generated from
Dataset: hsapiens_gene_ensembl
Description: Human genes (GRCh38.p14)
Version: GRCh38.p14

These genes were: EHMT2, DYNC1I2, CDKN1C, DUX4

BED File generated called: EwSAscGenes.bed

# Friday, October 24th

## Filtering a VCF File

We need to filter our VCF files to only include regions that our covered by EwS assiocated genes in our generated BED file

**ON MY LOCAL LAPTOP**
```
conda create --name ews
```

Possible Options:

### Bedtools

https://bedtools.readthedocs.io/en/latest/ 

```
conda install bioconda::bedtools
bedtools --version
# bedtools v2.31.1
```

```
bedtools intersect -a vcf_filtering_test_input.vcf.gz -b EwSAscGenes.bed -wa -u > partial_overlap.vcf
```

Doesn't seem to be outputting the correct output

### VCFTools

https://vcftools.github.io/index.html 

```
conda install bioconda::vcftools
vcftools --version
# VCFtools (0.1.17)
```
```
vcftools 
-gzvcf ______.vcf.gz (input vcf file)
-bed _____.bed (input bed file)
--remove-filtered-all (remove all variants that do have FILTER == "PASS)
--recode (create an output file) 
--stdout | (does not create a zipped file, put it into standard out)
gzip -c > _____.vcf.gz (zip the output filtered vcf file)
```
Does not include partial overlaps in the filtered file

### BCFTools

https://samtools.github.io/bcftools/bcftools.html

```
conda install bioconda::bcftools
bcftools--version                                            
# bcftools 1.22 
```

Requires files to be bgzip'ed and to have an index file

**CREATE INDEX**
```
tabix -p vcf ____.vcf,gz
```

```
bcftools 
view (command to filter a VCF file)
-R _____.bed (Filter variants based on the genes in the bed file)
-f PASS (remove variants that did not pass all filters)
-Oz (makes the output compressed)
-o _____.vcf.gz (name of the output file)
____.vcf.gz (vcf file we are filtering)
```

# Monday, October 27th

## Filtering the vcf files

Created new environment **ON TALAPAS** titled: ews

Installed BCFTools to that environment

Uploaded BED file to talapas

```
scp EwSAscGenes.bed joshkram@login.talapas.uoregon.edu:/projects/bgmp/shared/groups/2025/sarcoma/shared
```

Tried to run BCFTools on the files, but permission was denied. Trying to copy the files and see if that works

Copying the files and then running the above BCFTools command works

Created a new folder callecd EwS_filtered_struc_variants to hold the filtered files

Created an indexed file of each filtered vcf file using 

```
tabix -p vcf _____
```

For the cell line PDX305, after running bcftools i got an issue: [W::bgzf_read_block] EOF marker is absent. The input may be truncated
- I had accidently overwritten the file

| Cell Line | Variants Pre-Filter | Variants Post-Filter |
|-----------|---------------------|----------------------|
| A673      | 49659               | 151                  |
| A4573     | 51331               | 160                  |
| CHLA9     | 53595               | 164                  |
| CHLA10    | 60171               | 197                  |
| PDX305    | 53163               | 165                  |
| RDES      | 51205               | 166                  |
| SKNMC     | 49962               | 170                  |
| TC32      | 63315               | 200                  |
| TC71      | 52539               | 149                  |

## Creating a File of all of the Genes in each cell line found with the variants

Created a python script called variants.py

Takes all nine of the filtered VCF files and the BED file and creates two output files

One file has each cell line and the genes that were found in the area of the variants

The other file has the layout
GENE CELL LINE VARIANT TYPE

```
./variants.py -f1 filtered_struc_variants/filtered.A673.GRCh38.structural_variants.phased.vcf.gz -f2 filtered_struc_variants/filtered.A4573.GRCh38.structural_variants.phased.vcf.gz -f3 filtered_struc_variants/filtered.CHLA9.GRCh38.structural_variants.phased.vcf.gz -f4 filtered_struc_variants/filtered.CHLA10.GRCh38.structural_variants.phased.vcf.gz -f5 filtered_struc_variants/filtered.PDX305.GRCh38.structural_variants.phased.vcf.gz -f6 filtered_struc_variants/filtered.RDES.GRCh38.structural_variants.phased.vcf.gz -f7 filtered_struc_variants/filtered.SKNMC.GRCh38.structural_variants.phased.vcf.gz -f8 filtered_struc_variants/filtered.TC32.GRCh38.structural_variants.phased.vcf.gz -f9 filtered_struc_variants/filtered.TC71.GRCh38.structural_variants.phased.vcf.gz -o1 celllinesgenes.tsv -o2 genescelllinevariants.tsv -b EwSAscGenes.bed 
```

# Wednesday, October 29th

## Still creating a file of all genes in each cell line found with the variants

There is an issue with my script, not properly getting the end of the structural variant

Created a function to extract the length of the structural variant, and take its absolute value to find the end
- Deletions consider make the length negative

Final output seems good. Every non-header line in every file is assigned to a gene in the BED file

# Wednesday, November 5th

## PharmCat

Found a file within the pacbiowdlR directory for each cell line that creates a personalized summary that analyzes genetic variants within a genome to do precision medicine 


## Investigating chromatin and regulatory elements in EwS-assoicated gene regions in Fiber-Seq

https://fiberseq.github.io/ 

Installed fibertools to the environment "ews" on Talapas

```
conda install bioconda::fibertools-rs
ft --version
fibertools-rs 0.3.2 commit:
```

https://fiberseq.github.io/FIRE/docs/ 

My approach is to filter through the FIRE output peaks file, and extract regions that correspond to genes associated with EwS

See if there is a pattern of these genes being opened or closed across the cell lines, and how the structural variants impact that?

Wrote a script to do so called filterpeaks.py

Placing all filtered peak files into a directory called filteredpeaks

Moved the filteredpeaks directory to my local computer so I can do more investigation using RStudio

Created a new Rmd called openChromatin.Rmd to investigate genes considered to be in regions of open chromatin according to the FIRE outputs

ggplot2 version 4.0.0
tidyverse version 2.0.0
dplyr version 1.1.4
readxl version 1.4.5

After analysis, of the 120 EwS-associated genes we analyzed, 102 genes were found to lie on a region of open chromatin in all cell lines, 9 were found to lie on a region of closed chromatin in all cell lines, and 9 were variable across the cell lines

# Monday, November 10th

## Downloading Thejes's RDS Object

Thejes created an updated version of the RDS object with a new column for the intregrated data (integrated_cca) and another called seurat_clusters that contains information about the nine clusters identifed after intregration.

Need to download the object for enrichment analysis and to verify my chromatin architeture information (hopefully I did that correctly!!!!!)

Downloaded it to my local computer, but am putting it in a .gitignore so that it doesn't upload to GitHub

# Tuesday, November 11th

## Validating the chromatin findings

Put the R markdown in EwSProject/filteredpeaks/

Seurat Package version = ‘5.3.0’

Tidyverse Package version = '2.0.0'

Genes to investigate

CDKN1C
CDKN2A
CFKN2B
CTSD
MFNG
NFX2-2
NR0B1
PEG3
PPARGCA1A

Encountered an issue where the Seurat object labels everything as "EW" instead of its individual cell line which creates issues with visualizations. Asking Hope for help

# Wednesday, November 12th

## Continuing validating the chromatin findings

This reset the cell lines and put them towards their proper state

```
Idents(Ews) = Ews$cell_line
```

The following requested genes were not found: CFKN2B, NFX2-2, PPARGCA1A

Creating a plot of the gene expression data (RNA-seq data) and a plot of the gene matrix score (ATAC-seq data)

# Saturday, November 15th

## Creating all Known Genes BED File

After the meeting with Scott, he stated the intention of wanting to not solely focus on previously established EwS-assoicated genes. This will begin with creating a new BED file with all known human genes.

Created HumanGenes.Bed in BED-File/

Uploaded file to Talapas

## Filtering Variants within genes

To filter the VCF files for structural variants within genes

```
bcftools 
view (command to filter a VCF file)
-R _____.bed (Filter variants based on the genes in the bed file)
-f PASS (remove variants that did not pass all filters)
-Oz (makes the output compressed)
-o _____.vcf.gz (name of the output file)
____.vcf.gz (vcf file we are filtering)
```

To create a .tbi file which is necessary for accessing the VCF files

```
tabix -p vcf ____.vcf.gz
```

| Cell Line | Variants Pre-Filter | Variants Post-Filter |
|-----------|---------------------|----------------------|
| A673      | 49659               | 25732                  |
| A4573     | 51331               | 26516                  |
| CHLA9     | 53595               | 27564                  |
| CHLA10    | 60171               | 31111                  |
| PDX305    | 53163               | 27408                  |
| RDES      | 51205               | 26499                  |
| SKNMC     | 49962               | 25558                  |
| TC32      | 63315               | 32785                  |
| TC71      | 52539               | 26966                  |

Creating files that contain gene, cell line, variant info and variant type for further analysis

```
./variants.py -f1 filtered_struc_variants/genes.A673.GRCh38.structural_variants.phased.vcf.gz -f2 filtered_struc_variants/genes.A4573.GRCh38.structural_variants.phased.vcf.gz -f3 filtered_struc_variants/genes.CHLA9.GRCh38.structural_variants.phased.vcf.gz -f4 filtered_struc_variants/genes.CHLA10.GRCh38.structural_variants.phased.vcf.gz -f5 filtered_struc_variants/genes.PDX305.GRCh38.structural_variants.phased.vcf.gz -f6 filtered_struc_variants/genes.RDES.GRCh38.structural_variants.phased.vcf.gz -f7 filtered_struc_variants/genes.SKNMC.GRCh38.structural_variants.phased.vcf.gz -f8 filtered_struc_variants/genes.TC32.GRCh38.structural_variants.phased.vcf.gz -f9 filtered_struc_variants/genes.TC71.GRCh38.structural_variants.phased.vcf.gz -o1 genespercellline.tsv -o2 genecelllinevariant.tsv -b HumanGenes.bed 
```

INS = Insertion
DEL = Deletion
BND = Breakpoint
DUP = Duplication

# Monday, November 17th

## Analyzing the variants per gene per cell line

Created a new directory called Variant-Anaylsis and pulled the generated files from above to the new directory; however, the file is above the GitHub limit of 100 MB so it cannot be uploaded to Github

| Cell Line | Genes w/ Variants | 
|-----------|---------------------|
| A673      | 39169               |
| A4573     | 38251               | 
| CHLA9     | 39389               | 
| CHLA10    | 39213               | 
| PDX305    | 38846               |
| RDES      | 39439               | 
| SKNMC     | 38984               |
| TC32      | 39546               | 
| TC71      | 38389               |

| Cell Line | Unique Genes w/ Variants | 
|-----------|---------------------|
| A673      | 10               |
| A4573     | 50               | 
| CHLA9     | 47               | 
| CHLA10    | 1               | 
| PDX305    | 6               |
| RDES      | 77               | 
| SKNMC     | 14               |
| TC32      | 37               | 
| TC71      | 39               |


# Wednesday, November 19th

## Investigating methylation patterns in EWS-FLI1 fusion

Attempting to see if there is a difference in the methylation patterns of the wildtype versus fusion of the genes

Need to find a way to view the .bam files (they are so so big so they cannot be copied to my local computer)

This is not going well. I am going to email Kobi and try to get some clarification. 

# Friday, November 21st

## IGV

Downloaded IGV on Talapas in an environment called igv

# Monday. November 24th

## IGV 

```
conda install bioconda::igv
```

This ain't working. Anger

## Investigating other fusions

Continued my investigation ins the VariantAnalysis.Rmd

All from the filtered and annotated VCF file

| Cell Line | FLI1-Fusion Reads  | EWSR1-Fusion Reads  |
|---|---|---|
| A4573  | 4  | 4  |
| A673  | 4 |  4 |
| CHLA10 | 6 |  6 |
| CHLA9  | 2 | 2  |
| PDX305  | 4  | 4  |
| RDES  |  4 |  4 |
| SKNMC  |  4 | 4  |
| TC32 |  8 | 8  |
| TC71  |  4 |  4 |

Based on this, you need to have an equal amount of reads from both of the "fused" genes, and the range of reads goes from 2 to 8. This is a very broad category, but we can begin further analysis.

To investigate, I am going through each cell line's fusions, looking for genes that have a decent amount of fusion reads, and verifying if they have a corresponding gene that has the same number of fusions.

### A673

Possible Fusions of interest:

CHRDL2: 4 reads, but the reads correspond to two different genes (SUPT20H, STOML3) so probably fake

LINC00221: 4 reads, but the reads correspond to two different chromsomes (3, 16) so probably fake

HIVEP3-SUCLA2: 2 reads **POSSIBLE FUSION**

### A4573

**MAP2-PDE10A**: 4 reads of each gene, point to the same location -> **POSSIBLE FUSION?**

COL25A1: Could not find any corresponding gene that the reads matched to; probably fake

SH3D19: This was marked as a breakpoint, but was a mistake 

LINC01440: Could not find any corresponding gene that the reads matched to; probably fake

### CHLA9

EPHA3: Corresponded to multiple genes, probably fake

LINC01470: Corresponded to multiple genes, probably fake

SGCD: Didn't have a corresponding gene, probably fake

RIMS1: Corresponded to multiple genes, probably fake

MSL3-DT: Corresponded to multiple genes, probably fake

SPANXA2-OT1: Corresponded to multiple genes, probably fake

### CHLA10

HIVEP3-SUCLA2: 2 reads, also found in A673

HOWEVER, this was the same case in the A4573 cell line

CALM2-PCCA: 4 reads of each gene, point to the same location -> **POSSIBLE FUSION?**

RIMS1: Pointed to multple chromsomes (X, 7), so probably fake

TLK2: Could not find a corresponding gene, probably fake

LINC00221: 4 reads, but the reads correspond to two different chromsomes (3, 16) so probably fake

SPG7: 4 reads, but the reads correspond to two different chromsomes (3, 14) so probably fake

### PDX305

ZNF589: 4 reads, but the reads correspond to two different chromsomes (11, 22) so probably fake

SGCD: Could not find a corresponding gene, probably fake

MEI4: Could not find a corresponding gene, probably fake

PTPRR: 4 reads, but the reads correspond to two different chromsomes (3, X) so probably fake

### RDES

FAM242F: Points to two different genes at roughly the same place (MOB2, DNHD1), probably fake

LINC02735: FAKE

RNASEH2C-KAT5: **Possible fusion?**, only two reads and these reads map to the exact same starting and stopping point

### SKNMC

CNKSR2-KIF1B: **Possible fusion**, 4 reads that map together

YEATS2-GALNT13: **Possible fusion**, 4 reads that map together

MAGI3: No corresponding gene, probably fake

SGCD: No corresponding gene found, probably fake

DLG2: Inversion?

### TC32

LAMB4-ZMYM1: **Possible fusion**, 4 reads that map together

HIVEP3-SUCLA2: **Possible fusion**, Also found in CHLA10, A673

SGCD: No corresponding gene

CHRDL2: Matches to two genes in relatively close succession (SUPT20H, STOML3), probably fake 

SPG7: Maps to two different chromosomes (3, 14), probably fake

### TC71

LINC02487-IGFBP5: 4 matching reads. **POSSIBLE FUSION**

SEC24A: Couldn't find corresponding gene

CSMD3: Inversion? - chromosome 8 

TRPS1: Inversion? - chromosome 8

SNTB1: Inversion? - chromosome 8

PRELID2-ACACB: Two matching reads, **POSSIBLE FUSION**

TCTN1-EIF6: Four matching reads, **POSSIBLE FUSION**

MCF2L: No corresponding gene match

## Interesting Findings

In most cell lines, there was evidence of actual fusions; however, the majority of them, if they are real, are limited to a single cell line. Besides for the HIVE3P-SUCLA2 fusion which was found in three cell lines: A673, CHLA10, TC32

HIVEP3 - https://www.ncbi.nlm.nih.gov/gene/59269 

SUCLA2 - https://www.ncbi.nlm.nih.gov/datasets/gene/8803/ 

# Monday, December 1st

## Methylation continued

Making a Nextflow script to use SamTools to subset the haplotagged bam files to regions of interst

EWSR1
RS_2025_08	current	GRCh38.p14 (GCF_000001405.40)	22	NC_000022.11 (29268268..29300521)

RS_2025_08	current	GRCh38.p14 (GCF_000001405.40)	11	NC_000011.10 (128685132..128813267)

Subset to Chromosome 22 29200000 -> 29400000

Chromosome 11 128500000 -> 128900000

```
samtools --version
# samtools 1.22.1
nextflow -v
# nextflow version 25.10.2.10555
```

Created a Nextflow script called subsetregion.nf to subset the BAM files to regions of interest 

Copying the directory to the EWSProject directory

# Tuesday, December 2nd

## Methylation continued again

Counting the number of methylating bases, both 6mA and 5mC

| Cell Line | FLI1 Wild Type | FLI1 Fusion | EWSR1 Wild Type | EWSR1 Fusion |
|-----------|----------------|-------------|-----------------|--------------|
| A673      |   No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference          |
| A4573     | No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference          |
| CHLA9     | No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| CHLA10    | No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| PDX305    | No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| RDES      | No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| SKNMC     |  No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| TC32      |  No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 
| TC71      |  No obvious difference        |     No obvious difference         |      No obvious difference            |     No obvious difference 

# Saturday, December 27th

## Exploring CHLA9 v. CHLA10

Created UpSet Plot between the two cell lines

Having errors installing packages in R (computer broke sad)

Editting Nextflow script to subset haplotagged reads for the region of the SUCLA2 and HIVE3P jersey

Created new directory called HIVE3P_SUCLA2_Fusion that is located on Talapas. It is also on my local computer but it's too large to upload to GitHub.

# Monday, December 29th

## Exploring HIVE3P-SUCLA2 Fusion

Comparing the amount of methylated bases, both 6mA (open chromatin) and 5mC (methylation, usually upregulated) in wildtype, fusion and non-fusion

Fusion occured at Chromosome 1: 41542976 - Chromosome 13: 47972732

There does not appear to be any difference in chromatin openedness or methylated cytosines

I orginally had a table to organize my progress, but it was all similar so kinda a waste of space

