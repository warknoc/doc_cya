# doc_cya

> Zero-dependency offline pre-flight risk scanner for RFPs, MSAs, SOWs, and contractor agreements.

`doc_cya` runs locally against raw text files, Markdown, or `.docx` documents to detect predatory clauses, intellectual property grabs, uncapped liability, and administrative compliance gates before you spend hours drafting proposals or signing bad paper.

---

## What It Catches

* **Critical IP Forfeiture:** Work-made-for-hire claims, total assignment of rights/title/interest, background technology expropriation.
* **Severe Liability Landmines:** Uncapped liability, unilateral liquidated damages, asymmetric indemnity obligations.
* **Commercial Hazards:** Extreme payment terms (Net 60/90/120), termination for convenience without cost recovery, non-compete clauses.
* **Administrative Gates:** Mandatory security clearances (Secret, TS/SCI), CMMC/NIST standards, bonding thresholds.

---

## Why Local & Zero-Dependency?

Most enterprise contract analyzers require uploading sensitive documents, proprietary proposals, or unpublished patent filings to third-party cloud servers and LLMs. 

`doc_cya` runs entirely on your local machine using standard Python 3:
* **No external libraries:** Natively parses `.docx` files using built-in `zipfile` and `xml.etree`.
* **Zero API keys or telemetry:** Your contract text never leaves your memory space.
* **Instant runtime:** Audits large solicitation dumps in sub-second time.

---

## Quick Start

### 1. Download
```bash
curl -fsSL [https://raw.githubusercontent.com/warknoc/doc_cya/main/doc_cya.py](https://raw.githubusercontent.com/warknoc/doc_cya/main/doc_cya.py) -o doc_cya.py


# Scan a Word document
python doc_cya.py solicitation.docx

# Scan exported contract text or notes
python doc_cya.py agreement.txt



====================================================================
  DOC_CYA PRE-FLIGHT AUDIT: sample_agreement.docx
====================================================================

Audit Totals: 2 Critical | 1 Warning | 1 Gating Requirements

[CRITICAL]   Line 42    | Total IP Assignment
             Risk   : Demands complete transfer of title, ownership, and copyright.
             Context: "Vendor assigns all right, title, and interest in all developments..."

[CRITICAL]   Line 118   | Uncapped Liability
             Risk   : Explicit absence of standard commercial liability caps.
             Context: "Liability under this section shall be unlimited..."

[WARNING]    Line 88    | Extended Payment Terms
             Risk   : Extended payment schedule creates severe working capital delays.
             Context: "All undisputed invoices payable on Net 90 terms..."

[GATE]       Line 12    | Security Clearance
             Risk   : Mandatory active federal security clearance gate.
             Context: "Key personnel must maintain an active Secret clearance..."

--------------------------------------------------------------------
VERDICT: [CRITICAL RISK] PREDATORY CLAUSES / DEALBREAKERS DETECTED
====================================================================


Support & Open Source Tip Rail
doc_cya is open-source utility software licensed under MIT. If it saved you from a toxic contract or saved your team hours of review:

USDC / Ethereum: 0x9805F8fd4A23Dd39cce11c03C10e6f966B1D6755


License
MIT License. Free for commercial and private use.
