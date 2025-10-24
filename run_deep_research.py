"""Run a prompt against the OpenAI API for a list of company names.

This script reads a base prompt from a text file and a list of company names from a
CSV file. For each company, the prompt is formatted with the ``{company}`` or
``{company_name}`` placeholder and sent to the OpenAI API using the chatGPT 5Pro
model with Deep Research enabled. Results are written to STDOUT or, optionally,
to a specified output file.

Usage
-----
python run_deep_research.py --prompt-file prompt.txt --csv-file companies.csv \
    [--output results.txt]

Environment
-----------
The script expects the ``OPENAI_API_KEY`` environment variable to be set.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import List, Sequence

from openai import OpenAI

DEFAULT_MODEL = "chatgpt-5pro"


def read_prompt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SystemExit(f"Failed to read prompt file '{path}': {exc}") from exc


def read_company_names(path: Path) -> List[str]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            # Detect whether the file likely has a header by attempting to parse it
            try:
                handle.seek(0)
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames or []
                key = next((name for name in fieldnames if name), None)
                if key:
                    names = [str(row.get(key, "")).strip() for row in reader if row.get(key)]
                else:
                    raise ValueError
            except Exception:
                handle.seek(0)
                reader = csv.reader(handle)
                names = [row[0].strip() for row in reader if row and row[0].strip()]
    except (OSError, csv.Error, IndexError) as exc:
        raise SystemExit(f"Failed to read company CSV '{path}': {exc}") from exc

    filtered = [name for name in names if name]
    if not filtered:
        raise SystemExit("No company names found in CSV file.")
    return filtered


def format_prompt(base_prompt: str, company: str) -> str:
    if "{" in base_prompt and "}" in base_prompt:
        try:
            return base_prompt.format(company=company, company_name=company)
        except Exception as exc:
            raise SystemExit(
                "Failed to format prompt with company name. Make sure the prompt "
                "contains valid format placeholders (e.g., {company})."
            ) from exc
    return f"{base_prompt}\n\nCompany: {company}"


def call_openai(client: OpenAI, prompt: str, *, model: str = DEFAULT_MODEL, deep_research: bool = True) -> str:
    extra_body = {"deep_research": {"enabled": True}} if deep_research else None

    request_kwargs = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    }
    if extra_body:
        request_kwargs["extra_body"] = extra_body

    response = client.responses.create(**request_kwargs)

    parts: List[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                parts.append(content.text)
    output_text = getattr(response, "output_text", None)
    if not parts and output_text:
        parts.append(output_text)

    if not parts:
        raise RuntimeError("No textual content returned from OpenAI response.")

    return "".join(parts).strip()


def write_results(destination: Path | None, rows: Sequence[tuple[str, str]]) -> None:
    lines = [f"## {company}\n{result}\n" for company, result in rows]
    output = "\n".join(lines)
    if destination is None:
        print(output)
        return

    try:
        destination.write_text(output, encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Failed to write output file '{destination}': {exc}") from exc


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", required=True, type=Path, help="Path to the prompt .txt file")
    parser.add_argument("--csv-file", required=True, type=Path, help="Path to the CSV file containing company names")
    parser.add_argument("--output", type=Path, help="Optional file to store the combined results")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Override the OpenAI model name")
    parser.add_argument("--no-deep-research", action="store_true", help="Disable the Deep Research option")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])

    prompt_path: Path = args.prompt_file
    csv_path: Path = args.csv_file
    output_path: Path | None = args.output

    base_prompt = read_prompt(prompt_path)
    companies = read_company_names(csv_path)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("The OPENAI_API_KEY environment variable must be set.")

    client = OpenAI(api_key=api_key)

    results = []
    for company in companies:
        formatted_prompt = format_prompt(base_prompt, company)
        try:
            response_text = call_openai(
                client,
                formatted_prompt,
                model=args.model,
                deep_research=not args.no_deep_research,
            )
        except Exception as exc:
            raise SystemExit(f"Failed to fetch response for '{company}': {exc}") from exc
        results.append((company, response_text))

    write_results(output_path, results)


if __name__ == "__main__":
    main()
