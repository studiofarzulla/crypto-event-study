#!/usr/bin/env python3
"""
DOCX to Markdown converter
Parses the document.xml from extracted DOCX and converts to clean Markdown
"""

import xml.etree.ElementTree as ET
import re
import sys

# Namespaces used in DOCX XML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def get_text(element):
    """Extract all text from an element"""
    texts = []
    for t in element.findall('.//w:t', NS):
        if t.text:
            texts.append(t.text)
    return ''.join(texts)

def is_bold(run):
    """Check if run is bold"""
    bold = run.find('.//w:b', NS)
    return bold is not None

def is_italic(run):
    """Check if run is italic"""
    italic = run.find('.//w:i', NS)
    return italic is not None

def get_style(para):
    """Get paragraph style name"""
    style = para.find('.//w:pStyle', NS)
    if style is not None:
        return style.get('{%s}val' % NS['w'])
    return None

def is_heading(style):
    """Check if style is a heading"""
    if not style:
        return None
    if style.startswith('Heading'):
        # Extract level (Heading1 -> 1, Heading2 -> 2, etc.)
        match = re.search(r'Heading(\d+)', style)
        if match:
            return int(match.group(1))
    return None

def process_paragraph(para):
    """Process a paragraph and return markdown text"""
    style = get_style(para)
    heading_level = is_heading(style)

    # Get all runs in the paragraph
    runs = para.findall('.//w:r', NS)

    if not runs:
        return ''

    # Build paragraph text with formatting
    text_parts = []
    for run in runs:
        text = get_text(run)
        if not text:
            continue

        # Apply formatting
        if is_bold(run) and is_italic(run):
            text = f"***{text}***"
        elif is_bold(run):
            text = f"**{text}**"
        elif is_italic(run):
            text = f"*{text}*"

        text_parts.append(text)

    full_text = ''.join(text_parts).strip()

    if not full_text:
        return ''

    # Apply heading formatting
    if heading_level:
        return '#' * heading_level + ' ' + full_text

    return full_text

def process_table(table):
    """Process a table and return markdown table"""
    rows = table.findall('.//w:tr', NS)
    if not rows:
        return ''

    md_rows = []

    for i, row in enumerate(rows):
        cells = row.findall('.//w:tc', NS)
        cell_texts = []

        for cell in cells:
            # Get all paragraphs in cell
            cell_paras = cell.findall('.//w:p', NS)
            cell_text = ' '.join(get_text(p) for p in cell_paras).strip()
            cell_texts.append(cell_text)

        # Create markdown row
        md_row = '| ' + ' | '.join(cell_texts) + ' |'
        md_rows.append(md_row)

        # Add separator after first row (header)
        if i == 0:
            separator = '| ' + ' | '.join(['---'] * len(cell_texts)) + ' |'
            md_rows.append(separator)

    return '\n'.join(md_rows)

def convert_docx_to_markdown(xml_path):
    """Main conversion function"""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find the document body
    body = root.find('.//w:body', NS)
    if body is None:
        print("No body found in document", file=sys.stderr)
        return ''

    markdown_lines = []
    coversheet_count = 0
    in_coversheet = False
    page_break_count = 0

    for element in body:
        # Check for page breaks (potential coversheet boundaries)
        if element.tag == '{%s}p' % NS['w']:
            # Check if paragraph contains a page break
            if element.find('.//w:br[@w:type="page"]', NS) is not None:
                page_break_count += 1

                # First 3 page breaks likely indicate coversheets
                if page_break_count <= 3:
                    coversheet_count += 1
                    markdown_lines.append(f'\n<!-- COVERSHEET {coversheet_count} - TO BE REMOVED -->\n')
                    in_coversheet = True
                elif in_coversheet:
                    markdown_lines.append(f'\n<!-- END COVERSHEET {coversheet_count} -->\n')
                    in_coversheet = False

                markdown_lines.append('\n---\n')  # Page break

            # Process paragraph
            md_text = process_paragraph(element)
            if md_text:
                markdown_lines.append(md_text)
                markdown_lines.append('')  # Blank line after paragraph

        elif element.tag == '{%s}tbl' % NS['w']:
            # Process table
            md_table = process_table(element)
            if md_table:
                markdown_lines.append('')
                markdown_lines.append(md_table)
                markdown_lines.append('')

    return '\n'.join(markdown_lines)

if __name__ == '__main__':
    xml_path = '/home/kawaiikali/event-study/temp_docx_extract/word/document.xml'
    output_path = '/home/kawaiikali/event-study/dissertation-original.md'

    print(f"Converting {xml_path} to Markdown...")
    markdown = convert_docx_to_markdown(xml_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Conversion complete! Output: {output_path}")
    print(f"Lines generated: {len(markdown.splitlines())}")
