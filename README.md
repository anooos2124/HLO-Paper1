# HLO-Paper1
# Health Learning Ontology (HLO) — Paper 1 Research Artifacts

## Overview

This repository provides supporting research artifacts for the manuscript:

**LLM-Assisted Ontology Engineering for Context-Aware Medical Residency Education: Design and Evaluation of Health Learning Ontology**

Health Learning Ontology (HLO) is an OWL-based semantic representation designed to integrate biomedical and health-informatics knowledge with educational requirements and contextual dimensions relevant to medical residency learning.

The study combines biomedical knowledge reuse and re-engineering, LLM-assisted semantic enrichment, programmatic ontology construction, structural and logical validation, scenario-based functional assessment, and human semantic validation followed by expert-informed refinement.

## Repository Contents

### Supplementary S1 — HLO Ontology

`Supplementary_S1_Ontology/`

Contains the HLO OWL ontology artifact, including the refined and label-harmonized version:

`HLO_Template_LLM_v1.2_label_harmonized_2026-10-19.owl`

The ontology represents biomedical, educational, learner-related, and contextual concepts. The label-harmonized version addresses missing and duplicate primary labels.

### Supplementary S2 — LLM-Assisted Enrichment

`Supplementary_S2_LLM_Enrichment/`

Contains available prompt instructions and implementation materials associated with ontology enrichment:

- `HLO_DV3_LLM.execution_record.ipynb`
- `prompts.py`
- `enrichment_system.txt`

These files document available enrichment components and prompt-related instructions. They do not constitute a complete historical record of every GPT-4 API request and response.

### Supplementary S3 — Evaluation

`Supplementary_S3_Evaluation/`

Contains available evaluation notebooks, scripts, and recorded results, organized into two components.

**Learning-resource ranking:** Includes recorded baseline and enriched HLO evaluation scores, along with available notebooks for ranking evaluation and execution auditing.

**Ontology-level checks:** Includes scripts and notebooks for parent-placement and reference-code lookup assessments.

These components should be interpreted separately. The saved ranking results support verification of the reported aggregate statistics, but the available materials do not establish complete end-to-end reproduction of the original ranking runs from raw learning resources and independent relevance judgments.

## Evaluation Scope

The study reports structural and logical validation, scenario-based functional evaluation, and human semantic assessment involving seven experts.

The recorded functional comparison reports Top-1, Hit@3, Hit@5, mean reciprocal rank (MRR), and mean average precision (MAP) across 500 evaluation scenarios.

These evaluations assess the ontology and recorded scenario-based performance; they do not demonstrate improvements in real residents' educational outcomes or the performance of a deployed clinical learning system.

## Reproducibility and Provenance

The repository preserves available ontology, implementation, and evaluation artifacts for inspection and methodological transparency.

The presence of an implementation file does not by itself establish that the file generated a particular historical research result. Different evaluation workflows, including ontology-level checks and learning-resource ranking, are documented separately.

The repository should not be interpreted as providing a fully executable historical reconstruction of all GPT-4 enrichment calls or all original learning-resource ranking trials.

## Data and Ethical Considerations

Expert validation results are reported in the manuscript. Individual expert responses containing potentially identifying information are not publicly included in this repository.

## Related Manuscript

Submitted for consideration to *Semantic Web*.

## Contact

Enas M. Turki  
Department of Information Systems  
King Abdulaziz University  
Jeddah, Saudi Arabia
