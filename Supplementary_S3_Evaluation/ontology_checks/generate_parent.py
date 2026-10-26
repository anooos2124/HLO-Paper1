#!/usr/bin/env python3
"""Build the parent-placement scenario set from concepts shared by both ontology releases."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List

from rdflib import Graph, OWL, RDF, RDFS

SOURCE_VALUE = "HeTOP/EFMI/MIMO"


def _predicate(graph: Graph, local_name: str):
    return next((p for _, p, _ in graph if str(p).endswith("#" + local_name) or str(p).endswith("/" + local_name)), None)


def _first(graph: Graph, subject, predicate):
    if predicate is None:
        return ""
    value = next(graph.objects(subject, predicate), None)
    return str(value) if value is not None else ""


def _local(uri: str) -> str:
    return uri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _catalog(path: Path) -> Dict[str, dict]:
    graph = Graph()
    graph.parse(path)

    source_ontology = _predicate(graph, "sourceOntology")
    source_identifier = _predicate(graph, "sourceIdentifier")
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
        label = _first(graph, subject, pref_label) or _first(graph, subject, concept_name) or _first(graph, subject, RDFS.label)
        parents = [_local(str(p)) for p in graph.objects(subject, RDFS.subClassOf)]
        rows[sid] = {
            "source_identifier": sid,
            "label": label,
            "category": _first(graph, subject, concept_category),
            "parents": parents,
        }
    return rows


def generate(before_owl: Path, after_owl: Path, output_csv: Path, count: int = 300, seed: int = 73) -> List[dict]:
    before = _catalog(before_owl)
    after = _catalog(after_owl)

    candidates = []
    for sid in sorted(set(before) & set(after)):
        row = before[sid]
        if row["label"] and row["parents"]:
            candidates.append(row)

    if len(candidates) < count:
        raise ValueError(f"Need {count} shared parent candidates; found {len(candidates)}")

    rng = random.Random(seed)
    selected = rng.sample(candidates, count)
    selected.sort(key=lambda x: x["source_identifier"])

    records = []
    for i, row in enumerate(selected, 1):
        records.append({
            "scenario_id": f"P{i:03d}",
            "scenario_type": "parent_placement",
            "source_identifier": row["source_identifier"],
            "query": row["label"],
            "expected_label": row["label"],
            "expected_category": row["category"],
            "expected_parent": row["parents"][0],
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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument("--seed", type=int, default=73)
    args = parser.parse_args()
    rows = generate(args.before, args.after, args.output, args.count, args.seed)
    print(f"Parent scenarios: {len(rows)} -> {args.output}")


if __name__ == "__main__":
    main()
