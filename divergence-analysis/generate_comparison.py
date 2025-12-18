#!/usr/bin/env python3
"""
Generate side-by-side comparison of Gemini auto-cleanup vs manual cleanup.
Outputs as HTML and PDF.
"""

import difflib
from pathlib import Path

def generate_side_by_side_html(file1_path, file2_path, output_html):
    """Generate side-by-side HTML comparison."""

    # Read files
    with open(file1_path, 'r') as f:
        file1_lines = f.readlines()
    with open(file2_path, 'r') as f:
        file2_lines = f.readlines()

    # Generate HTML diff
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_file(
        file1_lines,
        file2_lines,
        fromdesc='Gemini 2.5 Flash Auto-Cleanup',
        todesc='Manual Cleanup',
        context=True,
        numlines=3
    )

    # Add custom styling for better readability
    custom_css = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            font-size: 11pt;
        }
        table.diff {
            border-collapse: collapse;
            width: 100%;
            border: 1px solid #ccc;
        }
        .diff_header {
            background-color: #e0e0e0;
            font-weight: bold;
            padding: 8px;
            text-align: center;
        }
        td.diff_header {
            border: 1px solid #999;
        }
        .diff_next {
            background-color: #c0c0c0;
        }
        .diff_add {
            background-color: #d4ffd4;
        }
        .diff_chg {
            background-color: #fff4b3;
        }
        .diff_sub {
            background-color: #ffd4d4;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #666;
            padding-bottom: 10px;
        }
        .stats {
            background-color: #f5f5f5;
            padding: 15px;
            border-left: 4px solid #4a90e2;
            margin: 20px 0;
        }
        .stats h2 {
            margin-top: 0;
            color: #4a90e2;
        }
    </style>
    """

    # Calculate stats
    file1_words = sum(len(line.split()) for line in file1_lines)
    file2_words = sum(len(line.split()) for line in file2_lines)
    file1_chars = sum(len(line) for line in file1_lines)
    file2_chars = sum(len(line) for line in file2_lines)

    word_diff = file2_words - file1_words
    char_diff = file2_chars - file1_chars
    word_pct = (word_diff / file1_words * 100) if file1_words > 0 else 0
    char_pct = (char_diff / file1_chars * 100) if file1_chars > 0 else 0

    stats_html = f"""
    <div class="stats">
        <h2>Comparison Statistics</h2>
        <ul>
            <li><strong>Gemini Auto-Cleanup:</strong> {file1_words} words, {file1_chars} characters</li>
            <li><strong>Manual Cleanup:</strong> {file2_words} words, {file2_chars} characters</li>
            <li><strong>Difference:</strong> {word_diff:+d} words ({word_pct:+.1f}%), {char_diff:+d} characters ({char_pct:+.1f}%)</li>
        </ul>
    </div>
    """

    # Insert custom CSS and stats before the table
    html_with_css = html_diff.replace('</head>', custom_css + '</head>')
    html_with_css = html_with_css.replace('<body>', f'<body><h1>Text Cleanup Comparison: Gemini vs Manual</h1>{stats_html}')

    # Write output
    with open(output_html, 'w') as f:
        f.write(html_with_css)

    print(f"HTML comparison saved to: {output_html}")
    return output_html, file1_words, file2_words, file1_chars, file2_chars


def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using weasyprint."""
    try:
        from weasyprint import HTML
        HTML(html_path).write_pdf(pdf_path)
        print(f"PDF saved to: {pdf_path}")
        return True
    except ImportError:
        print("weasyprint not available. Install with: pip install weasyprint")
        return False
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        return False


if __name__ == "__main__":
    base_dir = Path(__file__).parent

    gemini_file = base_dir / "text-samples" / "sample-1-gemini-auto-cleanup.txt"
    manual_file = base_dir / "text-samples" / "sample-1-manual-cleanup.txt"

    output_html = base_dir / "sample-1-comparison.html"
    output_pdf = base_dir / "sample-1-comparison.pdf"

    # Generate HTML
    generate_side_by_side_html(gemini_file, manual_file, output_html)

    # Convert to PDF
    html_to_pdf(output_html, output_pdf)
