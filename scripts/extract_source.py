"""Extract paragraphs from a docx file and split into chapter txt files.

Usage:
    python extract_source.py <input.docx> --output-dir <dir> [--start-para N] [--split-by-heading]

Reads a docx file, iterates paragraphs, and writes chapter-level txt files
based on Heading 1 boundaries. Each paragraph is prefixed with [NNN] index.
"""
import os
import sys
import argparse
from docx import Document


def extract(input_path, output_dir, start_para=0, split_by_heading=True):
    os.makedirs(output_dir, exist_ok=True)
    doc = Document(input_path)

    paragraphs = []
    current_chapter = []
    chapter_idx = 0
    chapter_title = "ch0_intro"

    for i, para in enumerate(doc.paragraphs):
        if i < start_para:
            continue
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name if para.style else ""

        # Detect heading
        if split_by_heading and "Heading 1" in style_name:
            # Save previous chapter
            if current_chapter:
                _save_chapter(output_dir, chapter_idx, chapter_title, current_chapter)
                chapter_idx += 1
            chapter_title = _sanitize_filename(text)
            current_chapter = []
        else:
            current_chapter.append(f"[{i}] {text}")

    # Save last chapter
    if current_chapter:
        _save_chapter(output_dir, chapter_idx, chapter_title, current_chapter)

    print(f"Extracted {chapter_idx + 1} chapters to {output_dir}")


def _sanitize_filename(text):
    """Convert heading text to safe filename."""
    import re
    safe = re.sub(r'[\\/:*?"<>|]', '_', text)
    return safe[:50]


def _save_chapter(output_dir, idx, title, lines):
    fname = f"ch{idx+1}_{title}.txt"
    fpath = os.path.join(output_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Chapter {idx+1}: {fname} ({len(lines)} paragraphs)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract docx to chapter txt files')
    parser.add_argument('input', help='Input docx file')
    parser.add_argument('--output-dir', default='source', help='Output directory')
    parser.add_argument('--start-para', type=int, default=0, help='Start paragraph index')
    parser.add_argument('--no-split', action='store_true', help='Do not split by heading')
    args = parser.parse_args()

    extract(args.input, args.output_dir, args.start_para, not args.no_split)
