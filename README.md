
# Multiomic Dissection of Chromatin Architecture and Transcriptional Programs in Ewing Sarcoma

Ewing sarcoma (EwS) is an aggressive pediatric cancer driven primarily by aberrant transcriptional activity of the **EWS::FLI1 fusion oncoprotein**. Despite this uniform genetic driver, EwS tumors display substantial **epigenetic and transcriptional heterogeneity**, suggesting additional elements influence tumor identity and behavior.

In collaboration with **Seattle Children’s Hospital** and **Fred Hutchinson Cancer Center**, we performed multi-omic analysis of **ATAC-seq**, **single-cell RNA-seq (scRNA-seq)**, and **Fiber-seq** data from **nine EwS tumor cell lines**. All sequencing data outputs were sent to **Talapas**, the University of Oregon’s high-performance computing cluster.

Our goal was to characterize how **chromatin architecture, structural variation, and transcriptional programs** individually or collectively interact to produce heterogeneity in EwS. An understanding of these mechanisms may enable the discovery of more robust diagnostic markers and inform the development of more effective, targeted therapeutic strategies for patients with Ewing Sarcoma.

---

## Repository Structure

### Variant-Analysis
Analysis of structural variants identified from Fiber-seq data, with a focus on how these variants influence chromatin architecture and gene expression.

### scAnalysis
Single-cell RNA-seq–based cell line and cell-type annotations, along with analysis of ATAC-seq data to evaluate differential chromatin accessibility across cellular states.

### FilteredPeaks
Examination of Fiber-seq–derived chromatin peaks to assess differences in chromatin accessibility across genomic regions and between cell lines.

### Halpotagged
Inspection of halpotagged Fiber-seq reads to investigate methylation patterns in:
- **Fusion genes vs. wild-type loci**
- Cell lines that are SV-positive vs. cell lines that are SV-negative

### VCF-Filter-Tests
Development and validation of filtering strategies to ensure accurate Variant Call Format (VCF) outputs derived from Fiber-seq data.

### BED-Files
Initial analyses focused on a curated set of **known EwS-associated genes**, later expanded to include **all genes**.

### Lab-Notebooks
Our research notebooks.
