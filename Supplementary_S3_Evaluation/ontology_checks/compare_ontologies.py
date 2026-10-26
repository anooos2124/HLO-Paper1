#!/usr/bin/env python3
"""Run the same scenario set against the before/after ontology releases and write paired results."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from rdflib import Graph, OWL, RDF, RDFS


def _predicate(graph: Graph, local_name: str):
    return next((p for _, p, _ in graph if str(p).endswith("#" + local_name) or str(p).endswith("/" + local_name)), None)


def _first(graph: Graph, subject, predicate):
    if predicate is None:
        return ""
    value = next(graph.objects(subject, predicate), None)
    return str(value) if value is not None else ""


def _local(uri: str) -> str:
    return uri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _load_scenarios(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _ontology_index(path: Path):
    graph = Graph()
    graph.parse(path)

    source_identifier = _predicate(graph, "sourceIdentifier")
    concept_code = _predicate(graph, "conceptCode")
    concept_name = _predicate(graph, "conceptName")
    concept_category = _predicate(graph, "conceptCategory")
    pref_label = _predicate(graph, "prefLabel")

    by_source: Dict[str, object] = {}
    by_code: Dict[str, object] = {}
    for subject in graph.subjects(RDF.type, OWL.Class):
        sid = _first(graph, subject, source_identifier)
        code = _first(graph, subject, concept_code)
        if sid:
            by_source[sid] = subject
        if code:
            by_code[code] = subject

    properties = {
        "sourceIdentifier": source_identifier,
        "conceptCode": concept_code,
        "conceptName": concept_name,
        "conceptCategory": concept_category,
        "prefLabel": pref_label,
    }
    return graph, by_source, by_code, properties


def _evaluate(path: Path, scenarios: List[dict], release_name: str) -> Tuple[List[dict], dict]:
    graph, by_source, by_code, props = _ontology_index(path)
    results = []

    for row in scenarios:
        stype = row["scenario_type"]
        sid = row["source_identifier"]
        subject = None
        resolved = False
        parent_match = ""
        reference_match = ""

        if stype == "parent_placement":
            subject = by_source.get(sid)
            resolved = subject is not None
            if resolved:
                parents = {_local(str(x)) for x in graph.objects(subject, RDFS.subClassOf)}
                parent_match = str(row.get("expected_parent", "") in parents)
                passed = parent_match == "True"
            else:
                passed = False
        elif stype == "reference_lookup":
            query = row.get("expected_concept_code") or row.get("query", "")
            subject = by_code.get(query)
            resolved = subject is not None
            if resolved:
                matched_sid = _first(graph, subject, props["sourceIdentifier"])
                reference_match = str(matched_sid == sid)
                passed = reference_match == "True"
            else:
                passed = False
        else:
            passed = False

        label = ""
        category = ""
        code = ""
        if subject is not None:
            label = _first(graph, subject, props["prefLabel"]) or _first(graph, subject, props["conceptName"]) or _first(graph, subject, RDFS.label)
            category = _first(graph, subject, props["conceptCategory"])
            code = _first(graph, subject, props["conceptCode"])

        results.append({
            "release": release_name,
            "scenario_id": row["scenario_id"],
            "scenario_type": stype,
            "source_identifier": sid,
            "resolved": str(resolved),
            "passed": str(passed),
            "parent_match": parent_match,
            "reference_match": reference_match,
            "resolved_label": label,
            "resolved_category": category,
            "resolved_concept_code": code,
        })

    counts = Counter(r["scenario_type"] for r in results)
    passed = Counter(r["scenario_type"] for r in results if r["passed"] == "True")
    summary = {
        "release": release_name,
        "triples": len(graph),
        "classes": len(set(graph.subjects(RDF.type, OWL.Class))),
        "source_identifier_values": sum(1 for _ in graph.triples((None, props["sourceIdentifier"], None))) if props["sourceIdentifier"] else 0,
        "concept_code_values": sum(1 for _ in graph.triples((None, props["conceptCode"], None))) if props["conceptCode"] else 0,
        "parent_cases": counts.get("parent_placement", 0),
        "parent_passed": passed.get("parent_placement", 0),
        "parent_accuracy": passed.get("parent_placement", 0) / counts.get("parent_placement", 1),
        "reference_cases": counts.get("reference_lookup", 0),
        "reference_passed": passed.get("reference_lookup", 0),
        "reference_accuracy": passed.get("reference_lookup", 0) / counts.get("reference_lookup", 1),
        "total_cases": len(results),
        "total_passed": sum(1 for r in results if r["passed"] == "True"),
        "overall_accuracy": sum(1 for r in results if r["passed"] == "True") / len(results),
    }
    return results, summary


def _write_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def compare(before_owl: Path, after_owl: Path, scenarios_csv: Path, output_dir: Path):
    scenarios = _load_scenarios(scenarios_csv)
    if len(scenarios) != 500:
        raise ValueError(f"Expected 500 scenarios; found {len(scenarios)}")

    before_rows, before_summary = _evaluate(before_owl, scenarios, "before")
    after_rows, after_summary = _evaluate(after_owl, scenarios, "after")

    _write_csv(output_dir / "before_results.csv", before_rows)
    _write_csv(output_dir / "after_results.csv", after_rows)

    keys = [k for k in before_summary.keys() if k != "release"]
    paired = []
    for key in keys:
        b = before_summary[key]
        a = after_summary[key]
        delta = a - b if isinstance(a, (int, float)) and isinstance(b, (int, float)) else ""
        paired.append({"metric": key, "before": b, "after": a, "difference": delta})
    _write_csv(output_dir / "comparison_summary.csv", paired)
    return before_summary, after_summary, paired


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--scenarios", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before, after, _ = compare(args.before, args.after, args.scenarios, args.output)
    print("Before:", before)
    print("After:", after)


if __name__ == "__main__":
    main()
