#!/usr/bin/env python3
"""
doc_cya: Offline Pre-Flight Risk Scanner for Solicitations, MSAs, SOWs, and IP Filings.
Zero external dependencies. Standard library only.
"""

import sys
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Rule definitions: (Severity, Category, Pattern, Explanation)
RULES = [
    # CRITICAL: Intellectual Property Seizure & Unlimited Exposure
    (
        "CRITICAL",
        "Work Made For Hire",
        r"\b(work(?:s)?\s+made\s+for\s+hire)\b",
        "Client claims statutory authorship/ownership over all generated work.",
    ),
    (
        "CRITICAL",
        "Total IP Assignment",
        r"\b(assign(?:s|ed|ing)?\s+all\s+right(?:s)?,\s+title(?:,)?\s+and\s+interest)\b",
        "Demands complete transfer of title, ownership, and copyright.",
    ),
    (
        "CRITICAL",
        "Background IP Forfeiture",
        r"\b(background\s+(?:ip|intellectual\s+property|technology|tools))\b.*?\b(vest(?:s)?|transfer(?:s)?|sole\s+property)\b",
        "Language potentially assigns or forfeits pre-existing background IP.",
    ),
    (
        "CRITICAL",
        "Uncapped Liability",
        r"\b(unlimited\s+liability)\b",
        "Explicit absence of standard commercial liability caps.",
    ),

    # WARNING: Harsh Commercial & Operating Terms
    (
        "WARNING",
        "Broad Indemnification",
        r"\b(defend,\s+indemnify(?:,)?\s+and\s+hold\s+harmless)\b",
        "Broad indemnity obligation. Ensure fault, negligence, or IP carve-outs exist.",
    ),
    (
        "WARNING",
        "Liquidated Damages",
        r"\b(liquidated\s+damages)\b",
        "Pre-set monetary penalties for schedule slips or performance issues.",
    ),
    (
        "WARNING",
        "Extended Payment Terms",
        r"\b(net\s+(?:60|90|120))\b",
        "Extended payment schedule creates severe working capital delays.",
    ),
    (
        "WARNING",
        "Termination For Convenience",
        r"\b(terminat(?:e|ion)\s+for\s+convenience)\b.*?\b(without\s+(?:cause|penalty|cost))\b",
        "Client can terminate contract at will without full cost recovery.",
    ),
    (
        "WARNING",
        "Non-Compete Clause",
        r"\b(covenant\s+not\s+to\s+compete|non-compete|shall\s+not\s+engage\s+in\s+any\s+competing)\b",
        "Restricts future commercial, engineering, or consulting operations.",
    ),

    # GATE: Mandatory Compliance & Administrative Barriers
    (
        "GATE",
        "Security Clearance",
        r"\b(active\s+(?:secret|top\s+secret|ts/sci))\b",
        "Mandatory active federal security clearance gate.",
    ),
    (
        "GATE",
        "Cybersecurity Maturity",
        r"\b(cmmc\s+(?:level\s+[23]|compliance)|nist\s+sp\s+800-171)\b",
        "Mandatory defense-grade cybersecurity compliance standard.",
    ),
    (
        "GATE",
        "Performance Bonding",
        r"\b(performance\s+bond|payment\s+bond|surety\s+bond)\b",
        "Requires securing surety/performance bonds prior to execution.",
    ),
]


def extract_text_from_docx(path):
    """Extracts raw paragraphs from a .docx file using native zip/xml parsing."""
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in tree.iterfind(".//w:p", namespace):
                texts = [node.text for node in p.iterfind(".//w:t", namespace) if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error parsing .docx: {e}")
        sys.exit(1)


def load_content(filepath):
    """Loads text from plain files (.txt, .md) or unpacks .docx files."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    if path.suffix.lower() == ".docx":
        return extract_text_from_docx(path)
    
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def scan_content(content):
    """Runs regex rules across lines and tracks hits with line numbers."""
    lines = content.splitlines()
    findings = []

    for rule_severity, category, pattern, description in RULES:
        regex = re.compile(pattern, re.IGNORECASE)
        for idx, line in enumerate(lines, start=1):
            clean_line = line.strip()
            if not clean_line:
                continue
            if regex.search(clean_line):
                findings.append({
                    "severity": rule_severity,
                    "category": category,
                    "line": idx,
                    "snippet": clean_line[:110],
                    "desc": description,
                })

    return findings


def print_report(filepath, findings):
    filename = Path(filepath).name
    border = "=" * 68

    print(f"\n{border}")
    print(f"  DOC_CYA PRE-FLIGHT AUDIT: {filename}")
    print(border)

    if not findings:
        print("\n[PASS] No critical red flags, predatory terms, or gates detected.\n")
        print(border + "\n")
        return

    crit_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARNING")
    gate_count = sum(1 for f in findings if f["severity"] == "GATE")

    print(f"\nAudit Totals: {crit_count} Critical | {warn_count} Warning | {gate_count} Gating Requirements\n")

    for f in findings:
        tag = f"[{f['severity']}]"
        print(f"{tag:<12} Line {f['line']:<5} | {f['category']}")
        print(f"             Risk   : {f['desc']}")
        print(f"             Context: \"{f['snippet']}\"\n")

    print("-" * 68)
    if crit_count > 0:
        print("VERDICT: [CRITICAL RISK] PREDATORY CLAUSES / DEALBREAKERS DETECTED")
    elif gate_count > 0:
        print("VERDICT: [GATE DETECTED] COMPLIANCE / CLEARANCE AUDIT REQUIRED")
    else:
        print("VERDICT: [CAUTION] OPERATIONAL WARNINGS DETECTED")
    print(border + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python doc_cya.py <file.txt | file.docx | file.md>\n")
        sys.exit(1)

    target_file = sys.argv[1]
    raw_text = load_content(target_file)
    matches = scan_content(raw_text)
    print_report(target_file, matches)
