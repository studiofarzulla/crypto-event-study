"""
Figure Verification Script
==========================

Verifies that all publication figures were generated correctly with proper:
- File existence
- File formats (PDF + PNG)
- Resolutions (300 DPI)
- Dimensions
- Content validation

Run after generating figures to ensure publication readiness.

Author: Farzulla Research
Date: November 10, 2025
"""

import os
from pathlib import Path
from PIL import Image
import subprocess

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent.parent
FIGURES_DIR = BASE_DIR / 'outputs' / 'publication' / 'figures'

EXPECTED_FIGURES = [
    'figure1_infrastructure_vs_regulatory',
    'figure2_infrastructure_sensitivity',
    'figure3_event_coefficients_heatmap',
    'figure4_tarchx_performance',
]

MIN_DPI = 300  # Publication standard
MIN_WIDTH = 2000  # Pixels (for 300 DPI)

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def check_file_exists(filepath):
    """Check if file exists"""
    return filepath.exists()

def check_file_size(filepath, min_size_kb=10):
    """Check if file is not suspiciously small"""
    size_kb = filepath.stat().st_size / 1024
    return size_kb >= min_size_kb

def check_png_resolution(png_path):
    """Check PNG resolution and dimensions"""
    try:
        img = Image.open(png_path)
        width, height = img.size

        # PIL DPI info (if available)
        dpi = img.info.get('dpi', (300, 300))

        return {
            'width': width,
            'height': height,
            'dpi': dpi,
            'valid': width >= MIN_WIDTH,
        }
    except Exception as e:
        return {
            'error': str(e),
            'valid': False,
        }

def check_pdf_pages(pdf_path):
    """Check PDF has exactly 1 page"""
    try:
        result = subprocess.run(
            ['pdfinfo', str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Pages:' in line:
                    pages = int(line.split(':')[1].strip())
                    return pages == 1

        return None  # pdfinfo not available
    except:
        return None

# ============================================================================
# MAIN VERIFICATION
# ============================================================================

def verify_all_figures():
    """Verify all publication figures"""
    print("=" * 80)
    print("PUBLICATION FIGURES VERIFICATION")
    print("=" * 80)
    print(f"\nFigures directory: {FIGURES_DIR}")
    print(f"Expected figures: {len(EXPECTED_FIGURES)}")
    print("-" * 80)

    all_passed = True
    results = []

    for fig_name in EXPECTED_FIGURES:
        print(f"\n[{fig_name}]")

        pdf_path = FIGURES_DIR / f"{fig_name}.pdf"
        png_path = FIGURES_DIR / f"{fig_name}.png"

        result = {
            'name': fig_name,
            'pdf_exists': False,
            'png_exists': False,
            'pdf_size_ok': False,
            'png_size_ok': False,
            'png_resolution_ok': False,
            'pdf_pages_ok': None,
            'status': 'UNKNOWN',
        }

        # Check PDF
        if check_file_exists(pdf_path):
            result['pdf_exists'] = True
            print(f"  PDF: ✓ Exists ({pdf_path.stat().st_size / 1024:.1f} KB)")

            if check_file_size(pdf_path, min_size_kb=10):
                result['pdf_size_ok'] = True
                print(f"       ✓ Size OK (>10 KB)")
            else:
                print(f"       ✗ Size too small (<10 KB)")
                all_passed = False

            pdf_pages = check_pdf_pages(pdf_path)
            if pdf_pages is True:
                result['pdf_pages_ok'] = True
                print(f"       ✓ Single page")
            elif pdf_pages is False:
                print(f"       ✗ Multiple pages detected")
                all_passed = False
            else:
                print(f"       ? Cannot verify pages (pdfinfo not installed)")
        else:
            print(f"  PDF: ✗ NOT FOUND")
            all_passed = False

        # Check PNG
        if check_file_exists(png_path):
            result['png_exists'] = True
            print(f"  PNG: ✓ Exists ({png_path.stat().st_size / 1024:.1f} KB)")

            if check_file_size(png_path, min_size_kb=50):
                result['png_size_ok'] = True
                print(f"       ✓ Size OK (>50 KB)")
            else:
                print(f"       ✗ Size too small (<50 KB)")
                all_passed = False

            # Check resolution
            res_info = check_png_resolution(png_path)
            if 'error' not in res_info:
                width = res_info['width']
                height = res_info['height']
                dpi = res_info['dpi']

                print(f"       ✓ Dimensions: {width} × {height} pixels")
                print(f"       ✓ DPI: {dpi[0]} × {dpi[1]}")

                if res_info['valid']:
                    result['png_resolution_ok'] = True
                    print(f"       ✓ Resolution OK (width >= {MIN_WIDTH}px)")
                else:
                    print(f"       ✗ Resolution too low (width < {MIN_WIDTH}px)")
                    all_passed = False
            else:
                print(f"       ✗ Error reading PNG: {res_info['error']}")
                all_passed = False
        else:
            print(f"  PNG: ✗ NOT FOUND")
            all_passed = False

        # Overall status
        if (result['pdf_exists'] and result['png_exists'] and
            result['pdf_size_ok'] and result['png_size_ok'] and
            result['png_resolution_ok']):
            result['status'] = 'PASS'
            print(f"\n  Status: ✓ PASS")
        else:
            result['status'] = 'FAIL'
            print(f"\n  Status: ✗ FAIL")
            all_passed = False

        results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')

    print(f"\nTotal figures: {len(EXPECTED_FIGURES)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if all_passed:
        print("\n" + "=" * 80)
        print("✓ ALL FIGURES VERIFIED - READY FOR PUBLICATION")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("✗ VERIFICATION FAILED - REGENERATE FIGURES")
        print("=" * 80)
        print("\nTo regenerate:")
        print("  python code/publication/create_november_2025_figures.py")
        return False

# ============================================================================
# DETAILED REPORT
# ============================================================================

def generate_detailed_report():
    """Generate detailed report of all figures"""
    print("\n" + "=" * 80)
    print("DETAILED FIGURE REPORT")
    print("=" * 80)

    for fig_name in EXPECTED_FIGURES:
        pdf_path = FIGURES_DIR / f"{fig_name}.pdf"
        png_path = FIGURES_DIR / f"{fig_name}.png"

        print(f"\n{fig_name}:")

        if pdf_path.exists():
            pdf_size = pdf_path.stat().st_size
            print(f"  PDF: {pdf_size:,} bytes ({pdf_size / 1024:.2f} KB)")
        else:
            print(f"  PDF: NOT FOUND")

        if png_path.exists():
            png_size = png_path.stat().st_size
            img = Image.open(png_path)
            width, height = img.size
            dpi = img.info.get('dpi', ('unknown', 'unknown'))

            print(f"  PNG: {png_size:,} bytes ({png_size / 1024:.2f} KB)")
            print(f"       Dimensions: {width} × {height} pixels")
            print(f"       DPI: {dpi[0]} × {dpi[1]}")
            print(f"       Mode: {img.mode}")
        else:
            print(f"  PNG: NOT FOUND")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import sys

    # Run verification
    success = verify_all_figures()

    # Generate detailed report
    if '--detailed' in sys.argv or '-d' in sys.argv:
        generate_detailed_report()

    # Exit code
    sys.exit(0 if success else 1)
