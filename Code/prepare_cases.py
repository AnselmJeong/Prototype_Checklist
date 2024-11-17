import re
import json
from pathlib import Path
from pymupdf4llm import to_markdown
from argparse import ArgumentParser


def convert_pdf_to_md(pdf_path: str, save: bool = False):
    md_text = to_markdown(pdf_path)
    if save:
        Path(pdf_path.replace(".pdf", ".md")).write_bytes(md_text.encode())
    return md_text


def split_chapters(md_text: str) -> list[dict]:
    chapters = []
    buffer = []
    prev_heading = None
    for line in md_text.splitlines():
        if line.startswith("## Chapter"):
            new_heading = re.sub(r"## Chapter \d+\. ", "", line)
            if buffer:
                chapters.append({"heading": prev_heading, "text": "\n".join(buffer)})
                buffer = []
            prev_heading = new_heading
        buffer.append(line)
    if buffer:
        chapters.append({"heading": prev_heading, "text": "\n".join(buffer)})
    return chapters


def remove_authors(text: str, length: int = 60):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if len(line) > length:
            return "\n".join(lines[i:])
    return text


def extract_diagnosis(text: str):
    pattern = r"• (.*?)\n"
    diagnoses = re.findall(pattern, text)

    return [diagnosis.strip() for diagnosis in diagnoses]


def extract_cases(md_text: str, heading: str):
    raw_texts = md_text.split("CCaassee")
    cases = []

    # Remove the first case

    for raw_text in raw_texts[1:]:
        raw_text = remove_authors(raw_text)
        diagnosis = extract_diagnosis(raw_text)
        stop_index = raw_text.index("DDiissccuussssiioonn")
        cases.append({"heading": heading, "diagnosis": diagnosis, "text": raw_text[:stop_index]})
    return cases


def main(pdf_path: str, markdown_path: str, save: bool = False):
    if pdf_path:
        md_text = convert_pdf_to_md(pdf_path, save)
    else:
        with open(markdown_path, "r") as file:
            md_text = file.read()

    chapters = split_chapters(md_text)
    all_cases = []
    for chapter in chapters:
        chapter_cases = extract_cases(chapter["text"], chapter["heading"])
        all_cases.extend(chapter_cases)

    output_path = Path(pdf_path).with_suffix(".json") if pdf_path else Path(markdown_path).with_suffix(".json")
    json.dump(all_cases, open(output_path, "w"))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--pdf_path", type=str, default=None)
    parser.add_argument("--md_path", type=str, default=None)
    parser.add_argument("--save", default=False, action="store_true")
    args = parser.parse_args()
    main(args.pdf_path, args.md_path, args.save)
