"""Fail a manuscript check on placeholders or numeric tokens lacking provenance."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PENDING_PATTERNS = (
    re.compile(r"\\PENDING\s*\{[^{}]*\}"),
    re.compile(r"⟨PENDING-[^⟩]+⟩"),
)
NUM_MACRO = re.compile(r"\\NUM\s*\{[^{}]+\}\s*\{[^{}]+\}")
REFERENCE_MACRO = re.compile(
    r"\\(?:ref|pageref|eqref|autoref|cite|citep|citet|label)\s*\{[^{}]*\}"
)
NUMBER = re.compile(r"(?<![\w\\])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?")
LABEL_CONTEXT = re.compile(
    r"(?:pp?\.?|pages?|sections?|secs?\.?|figures?|figs?\.?|tables?|equations?|eqs?\.?|§)\s*$",
    re.IGNORECASE,
)
LATEX_IDENTIFIER = re.compile(
    r"(?<![\w\\])(?:\\S\d+(?:\.\d+)*"
    r"|pp?\.[ \t~]+\d+(?:[ \t]*--[ \t]*\d+)?"
    r"|(?:Fig\.|Table|Sec\.)[ \t~]+\d+(?:\.\d+)*)"
    r"(?![\w.])",
    re.IGNORECASE,
)

WHITELIST = (
    "four-digit years 1900 through 2099",
    "page, section, figure, table, equation, and § identifiers immediately following their label",
    "numbers inside LaTeX ref/pageref/eqref/autoref/cite/citep/citet/label macros",
    "ddof0",
    "ddof1",
    "literal author-affiliation superscripts $^1$, $^2$, and $^{1*}$",
    "literal postal code 710049",
)

DDOF_LITERAL_TOKENS = frozenset(("ddof0", "ddof1"))
LITERAL_NUMERIC_TOKENS = frozenset(("$^1$", "$^2$", "$^{1*}$", "710049"))
# Detect candidates; only the two literal tokens above are exempt.
DDOF_CANDIDATE = re.compile(r"(?<![\w\\])ddof(?P<digits>[0-9]+)(?!\w)")


def masked_spans(text: str) -> list[tuple[int, int]]:
    spans = [match.span() for match in NUM_MACRO.finditer(text)]
    spans.extend(match.span() for match in REFERENCE_MACRO.finditer(text))
    spans.extend(match.span() for match in LATEX_IDENTIFIER.finditer(text))
    for token in LITERAL_NUMERIC_TOKENS:
        start = 0
        while (offset := text.find(token, start)) != -1:
            spans.append((offset, offset + len(token)))
            start = offset + len(token)
    return sorted(spans)


def mask_latex_comments(text: str) -> str:
    """Blank comments while preserving offsets and escaped percent signs."""
    characters = list(text)
    escaped = False
    in_comment = False
    for index, character in enumerate(text):
        if character in "\r\n":
            escaped = False
            in_comment = False
        elif in_comment:
            characters[index] = " "
        elif escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "%":
            characters[index] = " "
            in_comment = True
    return "".join(characters)


def is_masked(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(left <= start and end <= right for left, right in spans)


def whitelisted(text: str, match: re.Match[str]) -> str | None:
    token = match.group()
    plain = token.rstrip("%")
    if plain.isdigit() and 1900 <= int(plain) <= 2099:
        return "year"
    line_start = text.rfind("\n", 0, match.start()) + 1
    prefix = text[line_start : match.start()]
    if LABEL_CONTEXT.search(prefix[-32:]):
        return "page/section/figure/table/equation identifier"
    return None


def line_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    previous = text.rfind("\n", 0, offset)
    return line, offset - previous


def inspect(path: Path) -> list[str]:
    text = mask_latex_comments(path.read_text(encoding="utf-8"))
    findings: list[str] = []
    for pattern in PENDING_PATTERNS:
        for match in pattern.finditer(text):
            line, column = line_column(text, match.start())
            findings.append(
                f"{path}:{line}:{column}: PENDING_PLACEHOLDER: {match.group()}"
            )
    spans = masked_spans(text)
    for match in DDOF_CANDIDATE.finditer(text):
        if match.group() in DDOF_LITERAL_TOKENS:
            continue
        if is_masked(match.start(), match.end(), spans):
            continue
        line, column = line_column(text, match.start("digits"))
        findings.append(f"{path}:{line}:{column}: BARE_NUMBER: {match.group('digits')}")
    for match in NUMBER.finditer(text):
        if is_masked(match.start(), match.end(), spans):
            continue
        reason = whitelisted(text, match)
        if reason is not None:
            continue
        line, column = line_column(text, match.start())
        findings.append(f"{path}:{line}:{column}: BARE_NUMBER: {match.group()}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reject manuscript placeholders and numbers outside \\NUM{value}{source-pointer}."
    )
    parser.add_argument("files", nargs="*", type=Path, help="UTF-8 manuscript files")
    parser.add_argument(
        "--explain-whitelist", action="store_true", help="print the fixed exclusions"
    )
    args = parser.parse_args()
    if args.explain_whitelist:
        for entry in WHITELIST:
            print(entry)
    if not args.files:
        if args.explain_whitelist:
            return 0
        parser.error("at least one manuscript file is required")
    missing = [path for path in args.files if not path.is_file()]
    if missing:
        for path in missing:
            print(f"{path}: FILE_NOT_FOUND", file=sys.stderr)
        return 2
    findings = [item for path in args.files for item in inspect(path)]
    for item in findings:
        print(item)
    if findings:
        print(f"number gate failed: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print(f"number gate passed: {len(args.files)} file(s), 0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
