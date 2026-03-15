---
name: rxnim
description: "Parse chemical reaction images into machine-readable data (reactants, products, conditions) using the RxnIM multimodal LLM. Supports web API (Hugging Face Spaces) and local inference."
homepage: https://github.com/CYF2000127/RxnIM
---

# RxnIM Skill

Extract structured reaction data (SMILES, conditions) from chemical reaction images using the RxnIM model. RxnIM is a multimodal large language model designed for chemical reaction image parsing, achieving 84%-92% soft match F1 score on various benchmarks. It performs three tasks: reaction extraction, condition OCR, and role identification.

## Features

- **Image input**: PNG, JPG, etc.
- **Output**: JSON with reactants, products, conditions (reagents, solvents, temperature, yield).
- **Two modes**:
  1. **Web API**: Calls the Hugging Face Spaces demo (no local model needed).
  2. **Local inference**: Runs the full model locally (requires GPU and ~14 GB disk space).
- **Tasks supported**:
  - Reaction extraction (SMILES of reactants and products)
  - Condition OCR (text extraction and role labeling)
  - Role identification (reagent, solvent, temperature, yield)

## Background

RxnIM (Reaction Image Multimodal large language model) is the first multimodal LLM specifically designed to parse chemical reaction images into machine‑readable reaction data. It aligns task instructions with image features and uses an LLM‑based decoder to predict reaction components and conditions. The model is trained on a large‑scale synthetic dataset (Pistachio) and real ACS publications.

**Key capabilities**:
- Extracts SMILES of reactants and products with high accuracy.
- Interprets textual conditions (reagents, solvents, temperature, yield) and assigns roles.
- Outputs structured JSON or formatted reaction strings.
Performance: 84%–92% soft match F1 score on multiple test sets, outperforming previous methods.



##Quick Start
**Web API Mode (default)**
node scripts/rxnim.js --image /path/to/reaction.png

**Local Mode**
First, download the model checkpoint (see RxnIM repository(https://github.com/CYF2000127/RxnIM)) and set the environment variable RXNIM_MODEL_PATH.
export RXNIM_MODEL_PATH=/path/to/RxnIM-7b
node scripts/rxnim.js --image /path/to/reaction.png --mode local


##Installation##
**Dependencies**
pip install -r requirements.txt

For local mode, additional dependencies are required (see RxnIM repository(https://github.com/CYF2000127/RxnIM)).

**Model Download**
Web API: No download needed.
Local mode:
1.Download the checkpoint from Hugging Face(https://huggingface.co/datasets/CYF200127/RxnIM/blob/main/RxnIM-7b.zip).
2.Extract and set RXNIM_MODEL_PATH.

##Usage##
**Command Line**
node scripts/rxnim.js --image <path> [--mode web|local] [--output json|text]

**Output Example**
{
  "reactions": [
    {
      "reactants": ["CC(C)(C)OC(=O)N[C@H]1C=C[C@H](C(=O)O)C1"],
      "products": ["CC(C)(C)OC(=O)N[C@@H]1C[C@H]2C(=O)O[C@H]2[C@@H]1Br"],
      "conditions": {
        "reagents": ["Br2", "Pyridine"],
        "solvents": ["DME/H2O"],
        "temperature": "0-5°C",
        "yield": "68%"
      },
      "full_reaction": "CC(C)(C)OC(=O)N[C@H]1C=C[C@H](C(=O)O)C1>>CC(C)(C)OC(=O)N[C@@H]1C[C@H]2C(=O)O[C@H]2[C@@H]1Br | Br2, Pyridine[reagent], DME/H2O[solvent], 0-5°C[temperature], 68%[yield]"
    }
  ]
}

**Configuration**
Set environment variables:
-RXNIM_MODE: web or local (default: web)
-RXNIM_MODEL_PATH: Path to local model checkpoint (required for local mode)
-RXNIM_API_URL: Custom Web API endpoint (default: Hugging Face Spaces)

**Data Generation (Advanced)**
For training or generating synthetic reaction images, refer to the original RxnIM repository:
1.Datasets:
-Synthetic: Pistachio(https://huggingface.co/datasets/CYF200127/RxnIM/blob/main/reaction_images.zip)
-Real: ACS(https://huggingface.co/datasets/CYF200127/RxnIM/blob/main/reaction_images.zip)

2.Generation code: Located in data_generation/ directory of the repo. Requires original Pistachio dataset.

3.Model checkpoint: Download RxnIM-7b(https://huggingface.co/datasets/CYF200127/RxnIM/blob/main/RxnIM-7b.zip) for local inference.

##Limitations##
-Web API: Rate‑limited, requires internet.
-Local mode: Heavy resource requirements (GPU memory, disk space).
-Accuracy: Depends on image quality and complexity.

##References##
-RxnIM GitHub(https://github.com/CYF2000127/RxnIM)
-Hugging Face Spaces Demo(https://huggingface.co/spaces/CYF200127/RxnIM)
-Paper: Towards large‑scale chemical reaction image parsing via a multimodal large language model(https://doi.org/10.1039/D5SC04173B)
-ChemEAGLE (multi‑agent extension)(https://github.com/CYF2000127/ChemEagle)