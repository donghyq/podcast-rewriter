"""Combine podcast script sections into chapter-level files and generate Word docs.

Usage:
    python combine.py --base-dir <output_dir> --config <chapters.json>

Or with inline config (see CHAPTERS dict below for format reference).

The config JSON maps chapter output names to lists of input markdown files:
{
    "01_序言": ["script/01_序言.md"],
    "02_第一章": ["script/v4/ch1_01.md", "script/v4/ch1_02.md"],
    "全文": "ALL"  // special key to combine all chapters
}
"""
import os
import sys
import json
import argparse
import subprocess


def combine_files(file_list, output_path):
    """Combine multiple markdown files into one."""
    content = []
    for i, fpath in enumerate(file_list):
        if not os.path.exists(fpath):
            print(f"  WARNING: {fpath} not found, skipping")
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        content.append(text)
        if i < len(file_list) - 1:
            content.append("\n\n---\n\n")
    combined = "\n\n".join(content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(combined)
    size = os.path.getsize(output_path)
    print(f"  Combined: {output_path} ({size:,} bytes)")
    return output_path


def md_to_word(md_path, docx_path, md_to_word_script=None, python_exe=None):
    """Convert markdown to Word using md_to_word.py"""
    python = python_exe or sys.executable
    script = md_to_word_script or os.path.join(os.path.dirname(__file__), 'md_to_word.py')
    result = subprocess.run(
        [python, script, md_path, docx_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  Word: {docx_path}")
    else:
        print(f"  ERROR converting {md_path}: {result.stderr}")
    return docx_path


def run(base_dir, config_path, md_to_word_script=None, python_exe=None):
    with open(config_path, 'r', encoding='utf-8') as f:
        chapters = json.load(f)

    script_dir = os.path.join(base_dir, 'script')
    word_dir = os.path.join(base_dir, 'word_output')
    os.makedirs(word_dir, exist_ok=True)

    # Step 1: Combine sections into chapter-level markdown files
    print("=== Step 1: Combining sections into chapters ===")
    chapter_mds = []
    all_content = []

    for chapter_name, file_list in chapters.items():
        if file_list == "ALL":
            continue
        # Resolve relative paths
        resolved = [os.path.join(base_dir, f) if not os.path.isabs(f) else f for f in file_list]
        md_path = os.path.join(script_dir, f"{chapter_name}.md")
        combine_files(resolved, md_path)
        chapter_mds.append((chapter_name, md_path))

        with open(md_path, 'r', encoding='utf-8') as f:
            all_content.append(f.read().strip())

    # Step 2: Create full text combined markdown
    print("\n=== Step 2: Creating full text ===")
    full_md = os.path.join(script_dir, "全文_播客脚本.md")
    with open(full_md, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(all_content))
    full_size = os.path.getsize(full_md)
    print(f"  Full text: {full_md} ({full_size:,} bytes)")

    # Step 3: Generate Word files for each chapter
    print("\n=== Step 3: Generating Word files ===")
    for chapter_name, md_path in chapter_mds:
        docx_path = os.path.join(word_dir, f"{chapter_name}.docx")
        md_to_word(md_path, docx_path, md_to_word_script, python_exe)

    # Step 4: Generate combined Word
    print("\n=== Step 4: Generating combined Word ===")
    full_docx = os.path.join(word_dir, "全文_播客脚本.docx")
    md_to_word(full_md, full_docx, md_to_word_script, python_exe)

    print("\n=== Done! ===")
    print(f"Chapter Word files in: {word_dir}")
    print(f"Full text Word: {full_docx}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine podcast scripts and generate Word docs')
    parser.add_argument('--base-dir', required=True, help='Base output directory')
    parser.add_argument('--config', required=True, help='JSON config file mapping chapter names to file lists')
    parser.add_argument('--md-to-word', help='Path to md_to_word.py script')
    parser.add_argument('--python', help='Python executable path')
    args = parser.parse_args()

    run(args.base_dir, args.config, args.md_to_word, args.python)
