#!/usr/bin/env python3
"""
NCBI Multi-Database Search

Intelligent search across NCBI databases using E-Utilities API.
Automatically detects search intent and routes to appropriate database.

Supported databases:
- pubmed: Literature search
- gene: Gene information
- protein: Protein sequences
- nucleotide: Nucleotide sequences
- snp: SNP variants
- clinvar: Clinical variants
- taxonomy: Taxonomy

Usage:
    python ncbi_search.py "your query" [options]
    python ncbi_search.py "APOE gene" --db gene
    python ncbi_search.py "diabetes review" --db pubmed --years 5

Author: 亮子 (OpenClaw Assistant)
"""

import os
import sys
import json
import time
import argparse
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

# NCBI E-Utilities Base URLs
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ESEARCH_URL = f"{EUTILS_BASE}/esearch.fcgi"
ESUMMARY_URL = f"{EUTILS_BASE}/esummary.fcgi"
EFETCH_URL = f"{EUTILS_BASE}/efetch.fcgi"
ELINK_URL = f"{EUTILS_BASE}/elink.fcgi"

# Database configurations
DATABASES = {
    "pubmed": {
        "name": "PubMed",
        "description": "Biomedical literature",
        "keywords": ["paper", "article", "review", "publication", "journal", "study", 
                     "论文", "文献", "研究", "发表", "文章", "综述"],
        "id_field": "PMID",
        "link_template": "https://pubmed.ncbi.nlm.nih.gov/{}/",
    },
    "gene": {
        "name": "Gene",
        "description": "Gene information",
        "keywords": ["gene", "symbol", "编码", "基因", "mrna", "expression", "转录"],
        "id_field": "Gene ID",
        "link_template": "https://www.ncbi.nlm.nih.gov/gene/{}",
    },
    "protein": {
        "name": "Protein",
        "description": "Protein sequences",
        "keywords": ["protein", "peptide", "amino", "蛋白", "多肽", "氨基酸", "sequence"],
        "id_field": "Accession",
        "link_template": "https://www.ncbi.nlm.nih.gov/protein/{}",
    },
    "nucleotide": {
        "name": "Nucleotide",
        "description": "Nucleotide sequences",
        "keywords": ["nucleotide", "dna", "rna", "sequence", "genome", "cdna",
                     "核酸", "序列", "基因组"],
        "id_field": "Accession",
        "link_template": "https://www.ncbi.nlm.nih.gov/nuccore/{}",
    },
    "snp": {
        "name": "dbSNP",
        "description": "SNP variants",
        "keywords": ["snp", "variant", "polymorphism", "allele", "rs", 
                     "变异", "多态性", "突变"],
        "id_field": "rsID",
        "link_template": "https://www.ncbi.nlm.nih.gov/snp/{}",
    },
    "clinvar": {
        "name": "ClinVar",
        "description": "Clinical variants",
        "keywords": ["clinvar", "clinical variant", "pathogenic", "致病", "临床变异"],
        "id_field": "Variation ID",
        "link_template": "https://www.ncbi.nlm.nih.gov/clinvar/variation/{}",
    },
    "taxonomy": {
        "name": "Taxonomy",
        "description": "Taxonomy database",
        "keywords": ["species", "taxonomy", "organism", "classification", 
                     "物种", "分类", "物种分类"],
        "id_field": "TaxID",
        "link_template": "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id={}",
    },
    "biosample": {
        "name": "BioSample",
        "description": "Biological samples",
        "keywords": ["biosample", "sample", "样本"],
        "id_field": "Sample ID",
        "link_template": "https://www.ncbi.nlm.nih.gov/biosample/{}",
    },
    "assembly": {
        "name": "Assembly",
        "description": "Genome assemblies",
        "keywords": ["assembly", "genome assembly", "基因组组装"],
        "id_field": "Assembly ID",
        "link_template": "https://www.ncbi.nlm.nih.gov/assembly/{}",
    },
    "sra": {
        "name": "SRA",
        "description": "Sequence Read Archive",
        "keywords": ["sra", "sequencing", "reads", "测序数据"],
        "id_field": "SRA ID",
        "link_template": "https://www.ncbi.nlm.nih.gov/sra/{}",
    },
}

# Known gene symbols
GENE_SYMBOLS = [
    "APOE", "APP", "PSEN1", "PSEN2", "TREM2", "MAPT", "SNCA", "TARDBP",
    "BRCA1", "BRCA2", "TP53", "EGFR", "KRAS", "MYC", "PTEN", "VEGF",
    "IL6", "TNF", "IFNG", "IL1B", "IL10", "TGFB1", "BDNF", "NGF",
]

# Rate limiting
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 0.34
SESSION = None


def create_session():
    """Create a session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_api_key(args: argparse.Namespace) -> Optional[str]:
    """Get NCBI API key from args or environment."""
    if args.api_key:
        return args.api_key
    return os.environ.get("NCBI_API_KEY")


def rate_limit(api_key: Optional[str]):
    """Enforce rate limiting."""
    global LAST_REQUEST_TIME
    interval = 0.11 if api_key else MIN_REQUEST_INTERVAL
    elapsed = time.time() - LAST_REQUEST_TIME
    if elapsed < interval:
        time.sleep(interval - elapsed)
    LAST_REQUEST_TIME = time.time()


def detect_database(query: str) -> str:
    """
    Detect which NCBI database to search based on query.
    
    Priority:
    1. rs number pattern -> snp
    2. Gene symbols -> gene
    3. Database keywords
    4. Default -> pubmed
    """
    query_lower = query.lower()
    
    # Check for rs number (SNP)
    if re.search(r'\brs\d+\b', query_lower):
        return "snp"
    
    # Check for gene symbols
    words = re.findall(r'\b\w+\b', query)
    for word in words:
        if word.upper() in GENE_SYMBOLS:
            # If combined with paper keywords, still use pubmed
            if any(kw in query_lower for kw in ["paper", "article", "review", "论文", "文献"]):
                return "pubmed"
            return "gene"
    
    # Check database keywords
    db_scores = {}
    for db_name, db_info in DATABASES.items():
        score = 0
        for keyword in db_info["keywords"]:
            if keyword in query_lower:
                score += 1
        if score > 0:
            db_scores[db_name] = score
    
    # Return highest scoring database
    if db_scores:
        return max(db_scores, key=db_scores.get)
    
    # Default to PubMed
    return "pubmed"


def search_database(
    query: str,
    database: str,
    max_results: int = 10,
    api_key: Optional[str] = None,
    organism: Optional[str] = None
) -> Dict[str, Any]:
    """Search any NCBI database."""
    global SESSION
    if SESSION is None:
        SESSION = create_session()
    
    rate_limit(api_key)
    
    # Build query
    search_query = query
    
    # Add organism filter for gene database
    if database == "gene" and organism:
        search_query = f"({query}) AND {organism}[Organism]"
    
    params = {
        "db": database,
        "term": search_query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance"
    }
    
    if api_key:
        params["api_key"] = api_key
    
    response = SESSION.get(ESEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    result = data.get("esearchresult", {})
    
    return {
        "database": database,
        "query": search_query,
        "count": int(result.get("count", 0)),
        "ids": result.get("idlist", []),
    }


def fetch_summary(
    ids: List[str],
    database: str,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch summary for records using ESummary."""
    global SESSION
    if SESSION is None:
        SESSION = create_session()
    
    if not ids:
        return []
    
    rate_limit(api_key)
    
    params = {
        "db": database,
        "id": ",".join(ids),
        "retmode": "json"
    }
    
    if api_key:
        params["api_key"] = api_key
    
    response = SESSION.get(ESUMMARY_URL, params=params, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    result = data.get("result", {})
    
    records = []
    for id_ in ids:
        if id_ in result and isinstance(result[id_], dict):
            record = result[id_]
            record["_id"] = id_
            records.append(record)
    
    return records


def format_pubmed_results(records: List[Dict], total: int, query: str) -> str:
    """Format PubMed results."""
    lines = []
    lines.append("=" * 70)
    lines.append("PubMed Search Results")
    lines.append("=" * 70)
    lines.append(f"Query: {query}")
    lines.append(f"Total: {total} articles | Returned: {len(records)} articles")
    lines.append("=" * 70)
    
    for i, record in enumerate(records, 1):
        lines.append(f"\n[{i}] PMID: {record.get('_id', 'N/A')}")
        lines.append(f"Title: {record.get('title', 'N/A')}")
        
        authors = record.get("authors", [])
        if authors:
            author_names = [a.get("name", "") for a in authors[:5] if isinstance(a, dict)]
            author_str = ", ".join(author_names)
            if len(authors) > 5:
                author_str += f" et al."
            lines.append(f"Authors: {author_str}")
        
        # Extract year from pubdate
        pubdate = record.get("pubdate", "")
        year = pubdate.split()[0] if pubdate else "N/A"
        
        journal = record.get("fulljournalname", record.get("source", "N/A"))
        lines.append(f"Journal: {journal} ({year})")
        
        if record.get("doi"):
            lines.append(f"DOI: {record['doi']}")
        
        lines.append(f"URL: https://pubmed.ncbi.nlm.nih.gov/{record.get('_id')}/")
        lines.append("-" * 70)
    
    return "\n".join(lines)


def format_gene_results(records: List[Dict], total: int, query: str) -> str:
    """Format Gene results."""
    lines = []
    lines.append("=" * 70)
    lines.append("Gene Search Results")
    lines.append("=" * 70)
    lines.append(f"Query: {query}")
    lines.append(f"Total: {total} genes | Returned: {len(records)} genes")
    lines.append("=" * 70)
    
    for i, record in enumerate(records, 1):
        lines.append(f"\n[{i}] Gene ID: {record.get('_id', 'N/A')}")
        lines.append(f"Symbol: {record.get('name', 'N/A')}")
        lines.append(f"Description: {record.get('description', 'N/A')}")
        
        if record.get("chromosome"):
            lines.append(f"Chromosome: {record['chromosome']}")
        
        if record.get("organism"):
            organism = record["organism"]
            if isinstance(organism, dict):
                lines.append(f"Organism: {organism.get('scientificname', 'N/A')}")
            else:
                lines.append(f"Organism: {organism}")
        
        lines.append(f"URL: https://www.ncbi.nlm.nih.gov/gene/{record.get('_id')}")
        lines.append("-" * 70)
    
    return "\n".join(lines)


def format_snp_results(records: List[Dict], total: int, query: str) -> str:
    """Format SNP results."""
    lines = []
    lines.append("=" * 70)
    lines.append("dbSNP Search Results")
    lines.append("=" * 70)
    lines.append(f"Query: {query}")
    lines.append(f"Total: {total} variants | Returned: {len(records)} variants")
    lines.append("=" * 70)
    
    for i, record in enumerate(records, 1):
        snp_id = record.get("_id", "N/A")
        lines.append(f"\n[{i}] rsID: rs{snp_id}")
        
        if record.get("snp_id"):
            lines.append(f"Reference SNP: {record['snp_id']}")
        
        if record.get("genes"):
            genes = record["genes"]
            if isinstance(genes, list):
                gene_names = [g.get("name", "") for g in genes if isinstance(g, dict)]
                lines.append(f"Genes: {', '.join(gene_names)}")
        
        lines.append(f"URL: https://www.ncbi.nlm.nih.gov/snp/rs{snp_id}")
        lines.append("-" * 70)
    
    return "\n".join(lines)


def format_generic_results(records: List[Dict], total: int, query: str, database: str) -> str:
    """Format results for any database."""
    db_name = DATABASES.get(database, {}).get("name", database.upper())
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"{db_name} Search Results")
    lines.append("=" * 70)
    lines.append(f"Query: {query}")
    lines.append(f"Total: {total} records | Returned: {len(records)} records")
    lines.append("=" * 70)
    
    for i, record in enumerate(records, 1):
        lines.append(f"\n[{i}] ID: {record.get('_id', 'N/A')}")
        
        # Common fields
        if record.get("title"):
            lines.append(f"Title: {record['title']}")
        if record.get("name"):
            lines.append(f"Name: {record['name']}")
        if record.get("description"):
            lines.append(f"Description: {record['description']}")
        
        link_template = DATABASES.get(database, {}).get("link_template", "")
        if link_template:
            lines.append(f"URL: {link_template.format(record.get('_id', ''))}")
        
        lines.append("-" * 70)
    
    return "\n".join(lines)


def format_results(records: List[Dict], total: int, query: str, database: str) -> str:
    """Format results based on database type."""
    if database == "pubmed":
        return format_pubmed_results(records, total, query)
    elif database == "gene":
        return format_gene_results(records, total, query)
    elif database == "snp":
        return format_snp_results(records, total, query)
    else:
        return format_generic_results(records, total, query, database)


def main():
    parser = argparse.ArgumentParser(
        description="NCBI Multi-Database Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Literature search (auto-detect)
    %(prog)s "Alzheimer disease review"
    
    # Gene search (auto-detect)
    %(prog)s "APOE gene"
    
    # SNP search (auto-detect)
    %(prog)s "rs429358"
    
    # Specify database
    %(prog)s "APOE" --db gene --organism human
    %(prog)s "insulin" --db protein
    
    # PubMed with filters
    %(prog)s "diabetes" --db pubmed --years 5 --type review
        """
    )
    
    parser.add_argument("query", help="Search query")
    parser.add_argument("--db", choices=list(DATABASES.keys()), help="Database to search (auto-detected if not specified)")
    parser.add_argument("--max", type=int, default=10, help="Maximum results (default: 10)")
    parser.add_argument("--years", type=int, help="Years filter (PubMed only)")
    parser.add_argument("--type", help="Article type (PubMed only): review, clinical_trial, etc.")
    parser.add_argument("--organism", help="Organism filter (Gene only)")
    parser.add_argument("--format", choices=["json", "summary"], default="summary")
    parser.add_argument("--output", "-o", help="Save to file")
    parser.add_argument("--api-key", help="NCBI API key")
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    api_key = get_api_key(args)
    
    # Detect or use specified database
    database = args.db if args.db else detect_database(args.query)
    
    if args.verbose:
        print(f"Database: {DATABASES[database]['name']}", file=sys.stderr)
        print(f"Query: {args.query}", file=sys.stderr)
    
    # Build query with filters
    query = args.query
    
    # PubMed-specific filters
    if database == "pubmed":
        if args.years:
            end = datetime.now()
            start = end - timedelta(days=args.years * 365)
            query = f"({query}) AND {start.strftime('%Y/%m/%d')}:{end.strftime('%Y/%m/%d')}[PDat]"
        if args.type:
            type_map = {
                "review": "Review[pt]",
                "clinical_trial": "Clinical Trial[pt]",
                "randomized": "Randomized Controlled Trial[pt]",
                "meta_analysis": "Meta-Analysis[pt]",
            }
            if args.type in type_map:
                query = f"({query}) AND {type_map[args.type]}"
    
    # Search
    search_result = search_database(query, database, args.max, api_key, args.organism)
    ids = search_result["ids"]
    total = search_result["count"]
    
    if args.verbose:
        print(f"Found {total} results", file=sys.stderr)
    
    # Fetch summaries
    records = fetch_summary(ids, database, api_key) if ids else []
    
    # Format output
    output = format_results(records, total, query, database)
    
    # Print or save
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()