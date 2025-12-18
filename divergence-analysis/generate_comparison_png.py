#!/usr/bin/env python3
"""
Generate readable side-by-side PNG comparison of Gemini auto-cleanup vs manual cleanup.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

def wrap_text(text, width):
    """Wrap text to specified width."""
    lines = []
    for paragraph in text.split('\n'):
        if paragraph.strip():
            wrapped = textwrap.fill(paragraph, width=width)
            lines.extend(wrapped.split('\n'))
        else:
            lines.append('')
    return lines

def create_side_by_side_png(file1_path, file2_path, output_png):
    """Create a side-by-side PNG comparison."""

    # Read files
    with open(file1_path, 'r') as f:
        text1 = f.read()
    with open(file2_path, 'r') as f:
        text2 = f.read()

    # Settings
    font_size = 12
    line_height = 18
    column_width = 80  # characters
    padding = 40
    column_spacing = 40
    header_height = 100

    # Try to load a monospace font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        stats_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        stats_font = ImageFont.load_default()

    # Wrap text
    lines1 = wrap_text(text1, column_width)
    lines2 = wrap_text(text2, column_width)

    # Calculate dimensions
    max_lines = max(len(lines1), len(lines2))
    char_width = 8  # approximate width per character
    col_pixel_width = column_width * char_width

    img_width = padding * 2 + col_pixel_width * 2 + column_spacing
    img_height = header_height + padding * 2 + max_lines * line_height

    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw header
    draw.text((padding, 20), "Text Cleanup Comparison", font=header_font, fill='black')

    # Calculate stats
    words1 = len(text1.split())
    words2 = len(text2.split())
    chars1 = len(text1)
    chars2 = len(text2)
    word_diff = words2 - words1
    char_diff = chars2 - chars1
    word_pct = (word_diff / words1 * 100) if words1 > 0 else 0
    char_pct = (char_diff / chars1 * 100) if chars1 > 0 else 0

    stats_text = f"Gemini: {words1} words, {chars1} chars  |  Manual: {words2} words, {chars2} chars  |  Diff: {word_diff:+d} words ({word_pct:+.1f}%), {char_diff:+d} chars ({char_pct:+.1f}%)"
    draw.text((padding, 45), stats_text, font=stats_font, fill='#666666')

    # Draw column headers
    y_pos = header_height - 10
    draw.rectangle([padding, y_pos, padding + col_pixel_width, y_pos + 30], fill='#e8e8e8', outline='#999999')
    draw.rectangle([padding + col_pixel_width + column_spacing, y_pos, img_width - padding, y_pos + 30], fill='#e8e8e8', outline='#999999')

    draw.text((padding + 10, y_pos + 8), "Gemini 2.5 Flash Auto-Cleanup", font=stats_font, fill='black')
    draw.text((padding + col_pixel_width + column_spacing + 10, y_pos + 8), "Manual Cleanup", font=stats_font, fill='black')

    # Draw dividing line
    center_x = padding + col_pixel_width + column_spacing // 2
    draw.line([(center_x, header_height), (center_x, img_height - padding)], fill='#cccccc', width=2)

    # Draw text content
    y_pos = header_height + padding
    x1_pos = padding + 5
    x2_pos = padding + col_pixel_width + column_spacing + 5

    for i in range(max_lines):
        # Draw line number background
        if i % 5 == 0:
            draw.rectangle([padding, y_pos - 2, img_width - padding, y_pos + line_height - 2],
                          fill='#f9f9f9', outline=None)

        # Draw left column
        if i < len(lines1):
            draw.text((x1_pos, y_pos), lines1[i], font=font, fill='black')

        # Draw right column
        if i < len(lines2):
            draw.text((x2_pos, y_pos), lines2[i], font=font, fill='black')

        y_pos += line_height

    # Save
    img.save(output_png, 'PNG', quality=95, dpi=(150, 150))
    print(f"PNG comparison saved to: {output_png}")
    print(f"Image size: {img_width}x{img_height} pixels")


if __name__ == "__main__":
    base_dir = Path(__file__).parent

    gemini_file = base_dir / "text-samples" / "sample-1-gemini-auto-cleanup.txt"
    manual_file = base_dir / "text-samples" / "sample-1-manual-cleanup.txt"
    output_png = base_dir / "sample-1-comparison.png"

    create_side_by_side_png(gemini_file, manual_file, output_png)
