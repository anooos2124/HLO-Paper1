#!/usr/bin/env python3
"""Build the reference-lookup scenario set from reference codes available after enrichment."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List, Set

from rdflib import Graph, OWL, RDF, RDFS

SOURCE_VALUE = "HeTOP/EFMI/MIMO"


def _predicate(graph: Graph, local_name: str):
    return next((p for _, p, _ in graph if str(p).endswith("#" + local_name) or str(p).endswith("/" + local_name)), None)


def _first(graph: Graph, subject, predicate):
    if predicate is None:
        return ""
    value = next(graph.objects(subject, predicate), None)
    return str(value) if value is not None else ""


def _catalog(path: Path) -> Dict[str, dict]:
    graph = Graph()
    graph.parse(path)

    source_ontology = _predicate(graph, "sourceOntology")
    source_identifier = _predicate(graph, "sourceIdentifier")
    concept_code = _predicate(graph, "conceptCode")
    concept_name = _predicate(graph, "conceptName")
    concept_category = _predicate(graph, "conceptCategory")
    pref_label = _predicate(graph, "prefLabel")

    rows: Dict[str, dict] = {}
    for subject in graph.subjects(RDF.type, OWL.Class):
        if _first(graph, subject, source_ontology) != SOURCE_VALUE:
            continue
        sid = _first(graph, subject, source_identifier)
        if not sid:
            continue
        rows[sid] = {
            "source_identifier": sid,
            "label": _first(graph, subject, pref_label) or _first(graph, subject, concept_name) or _first(graph, subject, RDFS.label),
            "category": _first(graph, subject, concept_category),
            "concept_code": _first(graph, subject, concept_code),
        }
    return rows


def _used_ids(parent_csv: Path) -> Set[str]:
    if not parent_csv.exists():
        return set()
    with parent_csv.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["source_identifier"] for row in csv.DictReader(f)}


def generate(before_owl: Path, after_owl: Path, parent_csv: Path, output_csv: Path, count: int = 200, seed: int = 74) -> List[dict]:
    before = _catalog(before_owl)
    after = _catalog(after_owl)
    excluded = _used_ids(parent_csv)

    candidates = []
    for sid in sorted((set(before) & set(after)) - excluded):
        row = after[sid]
        if row["concept_code"] and row["label"]:
            candidates.append(row)

    if len(candidates) < count:
        raise ValueError(f"Need {count} reference candidates; found {len(candidates)}")

    rng = random.Random(seed)
    selected = rng.sample(candidates, count)
    selected.sort(key=lambda x: x["source_identifier"])

    records = []
    for i, row in enumerate(selected, 1):
        records.append({
            "scenario_id": f"R{i:03d}",
            "scenario_type": "reference_lookup",
            "source_identifier": row["source_identifier"],
            "query": row["concept_code"],
            "expected_label": row["label"],
            "expected_category": row["category"],
            "expected_concept_code": row["concept_code"],
            "selection_seed": seed,
        })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--seed", type=int, default=74)
    args = parser.parse_args()
    rows = generate(args.before, args.after, args.parent, args.output, args.count, args.seed)
    print(f"Reference scenarios: {len(rows)} -> {args.output}")


if __name__ == "__main__":
    main()
