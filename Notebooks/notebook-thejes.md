# Ewing Sarcoma Project

**Goal: Investigate chromatin structure and transcriptional programs in EwS**


## Week of 10/6

- Initial contact with collaborators
- 3 datasets:
    - scRNA-seq
    - scATAC-seq
    - Fiber-seq, long-read

## Week of 10/13

**9cl_seurat.rds**<br>
- Seurat dataset
- [Multiome dataset, Furlan lab](https://zenodo.org/records/12209095)
- [Github repo](https://github.com/furlan-lab/EwS_multiome)
- [Multimodal single-cell analyses reveal distinction fusion-regulated transcriptional programs in Ewing sarcoma](https://www.biorxiv.org/content/10.1101/2025.06.18.660457v1)
- Inspect Seurat object, with Seurat (scRNA-seq) and Signac (scATAC-seq)

Notes:
- Start looking at variants, assemble list of genes/genomic features with EwS associated variants
- Can query list as we find genes affected by structural variants, quickly tell if association is well-characterized or novel

---

Kobe initiated transfer of data onto Talapas (10/16)
- proj dir: /projects/bgmp/shared/groups/2025/sarcoma/
- data dir: /projects/bgmp/shared/groups/2025/sarcoma/shared
---

- Cell lines derived from patient samples
    - Fiber-seq
    - parallel scRNA/scATAC-seq
- Identify trends in gene expression, chromatin accessibility, and DNA methylation
- Data will most likely be given in processed form, will be responsible for initial QC filtering and analyzing datasets of sc data. 
- Fiber-seq will be in analyzable form

---
### R Resources

- [scRNA-seq, Seurat](https://satijalab.org/seurat/articles/get_started_v5_new)
- [scATAC-seq, Signac](https://github.com/GreenleafLab/ArchR)
- [scRNA + scATAC](https://stuartlab.org/signac/) combined data inside Seurat obj, use signac after
- [fiberseq](https://fiberseq.github.io/index.html)
- [Pacbio long read](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL)

## Exploratory data analysis



### 9 EwS CL

| Cell line                  | Tumor site                       | Fusion type |
|----------------------------|----------------------------------|-------------|
| A673                       | Muscle                           | 1           |
| A4573                      | Pleural effusion                 | 3           |
| CHLA9 (isogenic w/ CHLA10) | Thoracic lymph node              | 1           |
| CHLA10 (isogenic w/ CHLA9)  | Thoracic lymph node              | 1           |
| PDX305                     | Abdominal soft-tissue metastatis | 1           |
| RDES                       | Humerus                          | 2           |
| SKNMC                      | Retroorbital metastatis          | 1           |
| TC32                       | Illeum and adjacent soft tissues | 1           |
| TC71                       | Humerus                          | 1           |



## Week of 10/20

- Vini and Josh will be tackling generating the bed files and filtering vcf based on list of genes from literature (EwS associated genes)

- I will then be taking the filtered lists and utilizing that in scRNA-seq analsis in Seurat for DGE visualizations

**Goals:**
- Establish/plan a workflow
    - What are vcf files?
    - What are bed files? 
    - How are they related? 
    - Whats the purpose and importance for next step?
- Determine way to use RStudio in Talapas

---

### RStudio/Docker/Talapas...

- Troubleshooting with Jason
- Issues with *loading* Seurat, was able to install
    - unable to load libglpk.so.40
    - Jason ended up creating new docker file with Seurat already installed
    - `run_rstudio-prod-v04-thejes.sh` 
        - working script, made adjustments for our data dir and my username
- Jason also helped me create ssh keys for local and Talapas, so I won't need to keep using DUO. Can also ssh into specific nodes 

--- 

## Sat 10/25

- Jason fixed issue with loading Seurat library in RStudio/Talapas
- `run_rstudio_prod-v04-thejes.sh`
    - slurm-39479566.out
```bash
cat slurm-39479566.out

# copy and paste into terminal LOCALLY
ssh -L 55881:localhost:58091 tnair@login4.talapas.uoregon.edu -t ssh -L 58091:localhost:55881 n0349.talapas.uoregon.edu

# in new browser copy and paste, will be prompted to log into RStudio
# username/pw noted in .sh

http://localhost:55881
...
```

---

## Mon 10/27 

Josh and Vini finished generating filtered vcf files<br>

files located:<br>
`/projects/bgmp/shared/groups/2025/sarcoma/shared/filtered_struc_variants`

Files were filtered from the .structural_variants.phased.vcf<br> files located in:<br>
`/projects/bgmp/shared/groups/2025/sarcoma/shared/250711_lewings_lines/pacbiowdlR`


Investigated filtered vcf files

```bash
zcat filtered.A673.GRCh38.structural_variants.phased.vcf.gz | grep -v "^#" | cut -f8 | grep -o "SVTYPE=[^;]*" | sort | u
niq -c
```

```bash
8 SVTYPE=BND
71 SVTYPE=DEL
9 SVTYPE=DUP
63 SVTYPE=INS
```

Josh created two files for me:
1. Filtered genes per cell line (.txt)
- this is what will be used in scRNA-seq analysis
- contains all genes falling w/i or affected by variants
- will contain first instance of gene (no variant info, no duplicates)

ex:<br>
AG73<br>
gene1<br>
gene2<br>
gene3<br>

2. Filtered genes, cell line, variant type (.txt)
- future analysis so we can interpret expression results in the context of variant types
- will have duplicates

    |Case | Description | Example|
    |---|---|---|
    | 1| 1 gene, multiple SVs | Deletion + Inversion in same gene|
    | 2 | 1 SV, multiple genes| Large deletion removes mult. genes |
    |3 | Many genes, many SVs| Chromothripsis, "chromosome shattering" |

ex:<br>
gene, cell line, variant<br>
gene1, A673, DEL

---

## Wed 10/29

- Inspecting Seurat object in RStudio via Docker/Talapas
()

List of cell lines and genes
`/projects/bgmp/shared/groups/2025/sarcoma/shared/filtered_struc_variants/celllinesgenes.tsv`

celllinesgenes.tsv currently formatted like:
```
cell line 1
gene 1
gene 2
gene 3
cell line 2
gene 1
gene 2
cell line 3
gene 1
```
For ease of analysis, reformat in R to:
```
cell_line gene
1   gene 1
1   gene 2
2   gene 3
3   gene 4
```

```bash
grep -n "CHLA9" celllinesgenes.tsv

108:CHLA9
```

Reorganized `celllinesgenes.tsv` > `genes_by_cellline_clean.tsv` <br>

cell_line corresponding gene

NOTE:<br>
- When loading RDS obj in RStudio, error message:
```
Approaching session memory limit. Session memory used: 3,878 MiB, Limit: 4,096 MiB. System memory used: 16,339 out of 257,024 MiB (93% free).
```

Will need to increase mem in .sh script? **Will talk to Jason**
For now, will subset one cell line

```bash
ls -lh 9cl_seurat.rds

2.8G
```
Because readRDS() decompresses .rds object, amount of memory it's taking up greatly increases. Will need to scancel, increase mem to maybe 32GB? and submit a new sbatch.

Can't even subset, R won't load the obj at all without crashing/terminating session.<br>
For the time being will try and do things on local R Studio. Downloaded .rds and _clean.tsv

----
### SOFTWARE VERIONS


R version 4.5.1 (2025-06-13)<br>
Seurat 5.3.0

----

```r
seurat_ob #loaded Seurat object

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca

```

**Features:** genes<br>
**Active assay:MotifMatrix (870 features, 0 variable features):** dataset focused on analysis of transcription factor binding motifs, no highly variable motifs have been identified<br>


## Thur 10/30

Hope mentioned when she used Seurat for clustering etc required 36-50 CPU depending on what she did.

- Seurat uses variable amounts of memory
- Integration + clustering can be mem intensive
- BUT looking at marker genes and making plots is not
- pre-processing : 50 cpus per task
- integration: 36
- finding clusters, marker genes: 50
- plots, doable on personal laptop

our data may be less intensive because similar and fr same species than what Hope was doing

Looked at data locally:
- grouped cell lines, associated genes
- turned df into vectored list for each cell
- subsetted one cell line, was going to look at that initially
- BUT actually need to integrate and cluster data first

**Integrate and cluster data before moving on to gene expression** 

```r
seurat_obj

An object of class Seurat 
213408 features across 19737 samples within 4 assays 
Active assay: MotifMatrix (870 features, 0 variable features)
 2 layers present: counts, data
 3 other assays present: GeneExpressionMatrix, ATAC, GeneScoreMatrix
 2 dimensional reductions calculated: mo_UMAP, pca
```

- 213408 features across 19737 samples
    - features: genes, peaks, motifs, etc
    - samples: cell lines
- active assay: MotifMatrix
    - what assay Seurat is using BY DEFAULT 
- obj can store multiple layers (assays), each a diff modality (omic data layer)

| Assay | Data Source | Measures | Description |
|--|--|--|--|
| MotifMatrix | derived from ATAC |Motif enrichment | TF activity |
| GeneExpressionMatrix| RNA | gene expression  | what genes are transcribed, normalized expression
| ATAC| raw open-chromatin reads| Chromatin accessibility/open regions | peaks|
| GeneScoreMatrix| ATAC derived | pseudo-gene counts, accessibility around promoter regions| which genes are accessible *potentially* active|


## Sun, Mon 11/02-11/03

inspected metadata
- default assay is MotifMatrix, set default to "GeneExpressionMatrix"
- mo_UMAP is based on geneexpressionmatrix data!!!
    - naming convention seems misleading at first
    - pca based on geneexpresisonmatrix data as well
- Note 11/04: Data is NOT integrated or clustered (removed notes from this section that were wrong)

Next big step (after integrating/clustering, and top marker identification) is integrating the .tsv file vini and josh made and see where there's overlap

    1. look at RNAseq cluster markers to gene list .tsv (no variants)
        - see where there's overlap in expression/DE
    2. compare within cell lines
    3. compare across cell lines
    4. for OVERLAPPING genes
        - pull info from genes + variants.tsv
    5. pathway/GO enrichment (vini and josh)



## Tues 11/04

Met w/ Hope: still need to backtrack and integrate. Thought I didn't have to because saw clusters col in metadata but that's for UNINTEGRATED data. 

Workflow:
- integrate
- PCA
- UMAP
- neighbors
- cluster

Will also need to annotate cells, look in github script to see if there was annotation done? talk to kobe as well? (final stage clustering)
- what methods to use to cluster? 
    - singleR, cell x (?)

Then can switch back to unintegerated data for DGE

## Wed 11/05


Ran out of memory locally to split object for integration, switching back to docker/Talapas.

Updated run_rstudio...v04-thejes.sh to bump mem and cpus

```bash
#!/bin/bash
#SBATCH --account=bgmp<br>
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=12
#SBATCH --mem=64GB
#SBATCH --job-name=rstudio-prod
#SBATCH --signal=USR2@60
```

slurm-39767942.out

Integrated data, clusters reduced from 25-9. <br>UMAP visualizations and heatmap of distribution of cell lines amongst UMAP.

Still need to annotate cells


## Sun 11/09

- Find top up/down regulated markers
- Need to annotate data by DGE
- save dataframe/obj and transfer to Josh

- FindAllMarkers(log.fc = 0.25, min.pct = 0.1) based on prev. Seurat defaults and [HBC training guide](https://hbctraining.github.io/scRNA-seq/lessons/09_merged_SC_marker_identification.html)

----
### SOFTWARE VERSIONS

future 1.67.0

----

install.packages(future)

FindAllMarkers supports parallelization
library(future):<br>
performs computations in parallel
- output message about RStudio not able to use future command? I forgot to save the output

saved object/dataframe:<br>
/projects/bgmp/shared/groups/2025/sarcoma/shared/Multiome

output files:<br>
- cluster_markers.rds
- top100_upregulated
- top100_downregulated

handed over to josh to start w/ enrichment/pathway analyses <br>
in the meantime ill work on annotating and structural variant comparisons?

## Mon 11/10

- scale.data not needed for differential expression, pathway/enrichment analyses,
feature plots, violin plots, or dot plots
- scale.data IS needed for doheatmap visualizations of DEG or marker genes, 
PCA or regression on RNA data (if we re-run analyses)
- run scale.data on marker genes
    - for DoHeatMap() and any RNA PCA/regression workflow
    - NOT for dotplots, featureplots, or vlnplots, those use the data slot (which is log-normalized RNA data)

## Tues 11/11

Annotate in a two-pronged approach:
- Manual annotation: Identify biological programs (mechanisms) by looking at *known* phenotypic markers
    - ex: EWS::FLI1-high, mesenchymal-like, neural-like, proliferation...
    - defines cell states
- Automated annotation: Determine transcriptional programs (from DEGs)
    - quantitative assessment of gene modules/pathway signatures
- Goal: automated (transcriptional) should align with manual (biological)
    - ex: proliferation module and upregulation in proliferation genes
    - however, if proliferation module vs upregulation in mesenchymal-like genes...
        - would require further exploration

Automated annotation of genes (transcriptional programs) should match what mechanisms are identified (biological programs)

**Final approach:**<br>

After further thought decided to annotate based on 2 core EwS programs: 

1. Mesenchymal program
2. Neural program

Defined by HOXD13 transcription activity, outlined in [Apfelbaum et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9588607/#SD4) paper.

From Table S3. (overlap_up_with_HOXD13_kd sheets)
- HOXD13 and up/down regulated genes

**Mechanim summary:**<br>
EWS::FLI1 acts as both activator and repressor, HOXD13 counteracts repressor activity which enables mesenchymal programs

- HOXD13 is a transcription factor that promotes metastatic phenotypes
- **HOXD13 knockdown:** EWS::FLI1 expression fully effective -> *canonical/neural-like (fusion-high)* state
- **HOXD13 expressed:** EWS:FLI1 expression partially blocked -> *mesenchymal-like (fusion-low)* state


| Gene program| Phenotypic state | Key markers| Notes |
|--|--|--|--|
| EWS::FLI1<br> ("down regulated set") | Neural-like |--- | - "Canonical" identity<br>- Fusion active<br>- Differentiation associated<br>- maintain tumor cell identity and proliferation<br>- Low HOXD13 expression (knockout)|
| HOXD13<br> ("up regulated set") | Mesenchymal-like |--- | - Fusion-low <br>- counteracts repressor activity<br>- migratory driven program<br>- mesenchymal transition<br>- metastatic potential | 

Potential modifiers?

| Modifier | States | Markers |
| --| -- | -- |
| Proliferation | cell cycle stages | --- |

Tumor cells can co-exist across these two states within the same sample

Canonical (neural-like):<br> 
- "classic" state
- non-migatory, round, tightly packed, proliferative ("stem-like")
    - small round blue cell tumor: pathology 
    - undifferentiated and compact
    - high nuclear-cytoplasm ratio

Mesenchymal:<br>
- Migratory state, invasive 
- partially loses canonical signature so transcriptional activity looks less like classic EwS


## Sat-Mon 11/15-11/17

Apfelbaum 2022 paper:

Upregulated after HOXD13 KD:
- Belong to HOXD13 LOW, EWS::FLI1 HIGH
- "held-back" by HOXD13 expression 
- neural-like

Downregulated after HOXD13 KD:
- HOXD13 HIGH, EWS::FLI1 LOW
- require HOXD13 expression
- mesenchymal-like

| Cluster | Top markers (4 DEGs)          | Interpretation                                   |Label?                       |
| ------: | -------------------------------- | ---------------------------------------------------------------- | ------------------------------------- |
|       0 | FBXO32, MIR34AHG, TRIM22, ITGBL1 | Stress + ECM + muscle/atrophy → mesenchymal / ECM-ish, G1        | **Mes-like / ECM–stress**             |
|       1 | CAMK4, TP73, FAM111B, E2F2       | TP73/E2F2 → cell cycle & regulatory: HOXD13 mes-leaning     | **Mes-like / proliferative**          |
|       2 | PIF1, PSRC1, ARHGAP11B, APOLD1   | Mitotic / spindle / DNA replication + ARHGAP11B (progenitor)     | **Mitotic / proliferative**           |
|       3 | CIB4, IL1RAPL2, MROH2A, HS3ST2   | IL1RAPL2 & HS3ST2 → neural / synaptic: HOXD13 neural cluster     | **Neural-like**                       |
|       4 | IL3RA, SYT6, IER2, JUNB          | Immediate early (IER2, JUNB) + mixed signaling → stress/response | **Stress / mixed program**            |
|       5 | SYT4, PCDH15, BRINP3, SLC34A2    | Strongly neural (SYT4, PCDH15, BRINP3) + SLC34A2 (EMT-ish)       | **Neural-like / quiescent**           |
|       6 | PRLR, CRYBA2, HCN1, COL14A1      | HCN1 (neuronal) + COL14A1 (ECM) + S-phase-enriched cluster       | **Hybrid neural–mes / proliferative** |
|       7 | DMRT2, UNC13C, CCDC26, CA8       | Developmental TF (DMRT2) + neural/synaptic (UNC13C, CA8)         | **Developmental / neural-leaning**    |
|       8 | CENPF, MKI67, HIST1H2BN, HMMR    | Classic proliferation genes (Ki67, CENPF, histone, HMMR): G2M    | **Highly proliferative**              |


*CELL CYCLE STAGES*<br>
0: G1, WEAK MES<br>
1: S, MODERATE MES<br>
2: G2/M, AMBIGUOUS<br>
3: mixed, NEURAL-LIKE<br>
4: mixed, AMBIGUOUS<br>
5: G1, WEAK NEURAL<br>
6: S, WEAK MES<br>
7: mixed, AMBIGUOUS<br>
8: G2/M, WEAK NEURAL<br>

Proliferative: 1,2,6,8<br>
Low proliferation: 0,5<br>
Mixed: 3,4,7<br>

--- 
Confident programs:<br>
3: mixed, neural-like<br>
1: S, moderate mes<br>

Program exists, but weaker (remember this is all relative to other clusters):<br>
- weaker but not necessarily totally ambiguous(?)<br>
- provisionally labelled<br>

0: G1, weak mes<br>
5: G1, weak neural<br>
6: S, weak mes<br>
8: G2/M, weak neural<br>

Ambiguous:<br>
2: G2/M, ambiguous<br>
4, mixed, ambiguous<br>
7: mixed, ambiguous<br>


After feature plots and violin plots of some DEG markers:

Cluster 0 – identity markers: FBXO32, ITGBL1, TRIM22<br>
Cluster 1 – identity: CAMK4, FAM111B; proliferation: E2F2<br>
Cluster 2 – mitotic markers: PIF1, PSRC1, ARHGAP11B<br>
Cluster 3–7 – identity markers as listed<br>
Cluster 8 – proliferation markers: MKI67, CENPF, HIST1H2BN, HMMR




## Mon Mentor Mtg
After meeting with Kobe and showing annotations:


1. Take the gene sets from the HOXD13 paper I was referring to and MSigDb and create module scores (AddModuleScore()) <br>
2. Compare module scores across all clusters <br>
Use these scores to refine/validate the neural vs mesenchymal annotations

3. Will give more justification to annotations especially in addition to gene set enrichment analysis and GO pathway analysis
- still need to do GSEA and GO


## Summary ##

- used HOXD13/EWS::FLI1 axis to separate clusters into neural-like vs mesenchymal-like programs
- cell cycle scoring to identify proliferative clusters
- used cluster-specific top DEGs to verify cluster identity
- combined 3 to assign final cluster annotations

NEXT:<br>
module scores<br>
gene set enrichment analysis<br>
go pathway

compute module scores + run GSEA/GO to validate and refine cluster annotations, adjust labels if enrichment patterns disagree with the initial HOXD13/DEG/cell cycle assignments.


Additional next steps:

- Explore expression + accessibility of structural variant genes in scRNA-seq and scATAC-seq data
    - Feature/violin plots
- Gene set enrichment analysis
- Improve/validate annotations by using GSEA + AddModuleScore()


## Wed 11/19

slurm script is not bgmp/tnair bound?

so files were in home dir but not my bgmp dir<br>
cp -r all files

will eventually scancel job and relaunch apptainer after fixing run_rstudio script

Tinkering around with the slurm script<br>

need to bind the script to the right dir, right now it's set to home not project home<br>

- this way can access easily on vs code as well and is in sarcoma dir
- (technically can access ~ but this makes more sense ^)

```bash
cp -r /home/tnair/EwS/Seurat/. /projects/bgmp/shared/groups/2025/sarcoma/tnair/Seurat
```
In R studio console
```r
rstudioapi::openProject("~/EwS/Seurat")

rstudioapi::openProject("/projects/bgmp/tnair/bioinfo/Bi624/scRNAseq/scrnaseq-assignment-thejesnair")
```

## Fri 11/21

cluster_markers.rds

Used for:<n>
- GSEA
- GO
- KEGG
- pathway enrichment
- cluster annotation
(because GSEA/GO require ranked gene lists, not cell-level matrices)

Contains:

- all DEGs per cluster
- p-values, log2FC
- everything needed for enrichment analysis


integrated_seurat.rds

Used for:

- gene expression analysis of SV-affected genes

- comparing expression across cell lines

- comparing expression across clusters

- UMAP/FeaturePlot/VlnPlot
(because SV analysis needs actual expression values per cell)

Contains:

- full expression matrix

- metadata

- clusters

- UMAP/PCA

- integrated assay

----

- Vini is planning on looking at gene expression in genes containing structural variants
    - Put integrated_seurat.rds obj in shared folder
    - top 100 up/down regulated genes
    - /projects/bgmp/shared/groups/2025/sarcoma/shared/Multiome

## Sun-Mon, 11/23-11/24

Recapping:

What I've already done:
1. integrated + clustered
2. identifed top DEGs per cluster (up + down)
3. HOXD13 based neural/mesenchymal programs (Apfelbaum et al. 2022)
4. Added cell-cycle scoring: G1, S, G2/M
5. Combined HOXD13, cell-cycle stages
6. Tried validating a few markers to see expression across clusters

So annotations are a good starting point but want to support/validate approach so it's justified

- quantitative confirmation?

- Module scores (using AddModuleScore())
    - MSigDb
- GSEA
- GO enrichment
    - GSEA + GO makes sure that cluster labels align w/ known pathways

This will help 
- confirm neural/mesenchymal programs
- reveal hidden programs?
- resolved ambiguous clusters?

--- 

What I need to do next:<br>
1. Add module scores
2. Plot module scores along UMAPs
3. Run GSEA + GO enrichment
4. Refine annotation table
5. Create final UMAPs

Notes:
- Had to redo CellCycleScoring, I think the integratedCCA was the default.
    - integratedCCA has the corrected values (won't give us biological meaning)
- cell-cycle gene sets need to be evaluated on real expression (biological scoring)


- Plots didn't change
- Cell cycle staging values didn't change.
- Default set to GeneExpressionMatrix for cell-cycle staging, then changed back to integratedCCA when making labelled umaps (HOXD13 + phase)

---
### MSigDb

[MSigDb](https://www.gsea-msigdb.org/gsea/msigdb/)

[Collections](https://www.gsea-msigdb.org/gsea/msigdb/human/collections.jsp#H)<br>
- Hallmark gene sets
    - HALLMARK_EPITHELIAL_MESENCHYMAL_TRANSITION
        - EMT (epithelial mesenchymal transition)
            - process involved in many things including metastasis
            - when epithelial cells gain migratory, mesenchymal features
    - HALLMARK_G2M_CHECKPOINT
        - G2M checkpoint
            - proliferation markers (mitotic activity)
    - HALLMARK_E2F_TARGETS
        - E2F
            - targets E2F transcription factors
            - EWS::FLI interact with E2F tf
            - E2F: S-phase entry

    - 
- Gene ontology gene sets (C5)<br>

UP
- GOBP_NEUROGENESIS
- GOBP_NEURON_DIFFERENTATION
- GOBP_NEURON_DEVELOPMENT
- GOBP_NEURAL_CREST_CELL_FATE_COMMITMENT

DOWN
- GOBP_EXTRACELLULAR_MATRIX_ORGANIZATION
- GOBP_BIOLOGICAL_ADHESION
- GOBP_CELL_MIGRATION
- GOBP_MESENCHYME_DEVELOPMENT



https://satijalab.org/seurat/reference/integratedata
https://satijalab.org/seurat/articles/seurat5_integration


#### Git note
```bash
git add Notebooks/notebook-thejes.md 
git commit -m "Update lab notebook"
git pull --rebase origin main
git push origin main
```


GO, GSEA:<br>
install clusterProfiler
```R
install.packages("BiocManager")
library(BiocManager)
```

----
### SOFTWARE VERIONS


Bioconductor version 3.22 (BiocManager 1.30.27), R 4.5.1 (2025-06-13)

----

Issues installing clusterProfiler:

> .libPaths()
[1] "/home/tnair/R/rocker-rstudio/4.5.1" "/usr/local/lib/R/site-library"      "/usr/local/lib/R/library"


ERROR:
```R
io_utils.c:16:10: fatal error: zlib.h: No such file or directory
...
ERROR: compilation failed for package ‘XVector’
```

Apptainer container is missing system libraries (zlib.h)<br>
So then other libraries cannot be installed. clusterProfiler and all its dependencies failed to install, even when using personal R library path. I would have to rebuild container or use a module with Bioconductor preinstalled.

Easier to just work locally, which is fine because computationally intensive work is already finished.

## Sun-Mon, 11/30-12/1

cluster annotations<br>
neural:
- genes involves in neurons
- synaptic signaling
- neuronal differentiation
- neural maturation

clusters: 3,5

neural-crest:
- different than neural program
- early developmental genes
- progenitor-like genes

cluster: 7

mixed neural/mes:
- not strongly lineage specific
- both neural-like and mesenchymal-like DEGs present

cluster: 6

* if we look at the heatmap the profiles of 6 and 7 look similar

remember:
- heatmap is using those GO pathways, so captures broad pathway activity, but doesnt necessarily specifiy lineage-defining marker genes
- 7 expresses neural-crest and developmental regulators (DMRT2, UNC13C, CA8), supporting a neural crest-like identity
- 6 shows a mix of weak neural, mesenchymal, and proliferative genes. 

So, final annotations integrate both pathway-level signals and specific marker genes


FINAL ANNOTATIONS

| Cluster | Final label                             |
| ------- | --------------------------------------- |
| 0       | Stress-like                             |
| 1       | Mesenchymal-like                        |
| 2       | Mesenchymal-like (highly proliferative) |
| 3       | Neural-like                             |
| 4       | Stress-like                             |
| 5       | Neural-like                             |
| 6       | Mixed neural/mes                        |
| 7       | Neural crest-like                       |
| 8       | Highly proliferative                    |

| Cluster | Final label                             | Proliferation tier |
| ------- | --------------------------------------- | ------------------ |
| 0       | Stress-like                             | Low                |
| 1       | Mesenchymal-like                        | High               |
| 2       | Mesenchymal-like (highly proliferative) | Very high          |
| 3       | Neural-like                             | High               |
| 4       | Stress-like                             | Intermediate       |
| 5       | Neural-like                             | Low                |
| 6       | Mixed neural/mes                        | High               |
| 7       | Neural crest-like                       | Intermediate       |
| 8       | Highly proliferative                    | Very high          |




(primary) marker genes = what the cluster is defined by
(secondary) module scores = what major program the cluster is running
(tertiary) GO = broad context

### Module Score Summary (per cluster)

Columns:
- HOXD13_neural (Apfelbaum neural-like program)
- HOXD13_mes (Apfelbaum mesenchymal-like program)
- G2M (G2/M checkpoint)
- E2F (DNA replication / E2F targets)
- EMT (Hallmark EMT)

Cluster | HOXD13_neural | HOXD13_mes | G2M     | E2F      | EMT
--------|----------------|-------------|---------|----------|---------
0       | –0.077         | +0.052      | +0.001  | –0.069   | +0.022
1       | –0.106         | +0.030      | +0.182  | +0.176   | +0.004
2       | –0.122         | +0.077      | +0.265  | +0.174   | +0.019
3       | +0.097         | –0.143      | +0.149  | +0.134   | –0.033
4       | –0.054         | –0.013      | +0.110  | +0.049   | +0.016
5       | –0.079         | +0.035      | –0.015  | –0.085   | –0.015
6       | –0.023         | –0.141      | +0.197  | +0.184   | –0.056
7       | –0.025         | –0.112      | +0.108  | +0.097   | –0.044
8       | –0.023         | –0.081      | +0.229  | +0.199   | +0.020

- cluster 3, strongly positive neural program
- cluster 5, neural from DE marker genes, shows weaker program activation, lower (negative) proliferation scores
- clusters 2,8: strong positive G2M/E2F and DE markers are cell cycle assoc.
- clusters 1,6,3: strong proliferation, but not cell-cycle identity
- cluster 4: stress-like, mod proliferation
- cluster 7: neural crest-like, mod proliferation
- cluster 0: stress like, low prolif
- cluster 5: neural-like, lowest proliferation amongst all clusters (negative values)


### saved integratd obj with final annotations as 'seurat_integration_finalannotations.rds'

size: 3.2G<br>
contains all assays/layers/modules

### saved rna-assay only integrated obj as 'seurat_rna_only_forGSEA_GO.rds'
For GO/GSEA analyses, I only need RNA assay and annotations, so saving another object so I can work on these tasks locally

size: 342M<br>


cancelled slurm-apptainer job (39767942) since all computationally intensive steps (integration, clustering, marker identification, annotation...) are complete; remaining analyses will be done locally
