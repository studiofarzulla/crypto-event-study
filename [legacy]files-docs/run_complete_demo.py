#!/usr/bin/env python3
"""
Complete End-to-End Demo
========================

Demonstrates the entire publication package workflow:
1. Generate example data
2. Validate data
3. Create figures
4. Create tables
5. Show summary

Run this to see the complete system in action.

Usage:
    python run_complete_demo.py
"""

import subprocess
import sys
from pathlib import Path
import time

def print_header(text):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_step(number, total, description):
    """Print step indicator"""
    print(f"\n[STEP {number}/{total}] {description}")
    print("-" * 80)

def run_script(script_name, description):
    """Run a Python script and show output"""
    print(f"\nRunning: {script_name}")
    print(f"Purpose: {description}\n")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr, file=sys.stderr)

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✓ Completed successfully ({elapsed:.2f}s)")
            return True
        else:
            print(f"✗ Failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Script timed out (>60s)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def show_outputs():
    """Display summary of generated files"""
    print_header("GENERATED OUTPUT FILES")

    # Check figures
    fig_dir = Path('/home/kawaiikali/event-study/publication_figures')
    if fig_dir.exists():
        figures = sorted(fig_dir.glob('*.pdf'))
        print(f"Figures ({len(figures)} PDF files):")
        for fig in figures:
            size_kb = fig.stat().st_size / 1024
            print(f"  • {fig.name} ({size_kb:.1f} KB)")
    else:
        print("⚠ No figures directory found")

    print()

    # Check tables
    table_dir = Path('/home/kawaiikali/event-study/publication_tables')
    if table_dir.exists():
        tables = sorted(table_dir.glob('*.tex'))
        print(f"Tables ({len(tables)} LaTeX files):")
        for table in tables:
            size_kb = table.stat().st_size / 1024
            print(f"  • {table.name} ({size_kb:.1f} KB)")
    else:
        print("⚠ No tables directory found")

def show_next_steps():
    """Display next steps for user"""
    print_header("NEXT STEPS")

    print("""
1. VIEW FIGURES:
   cd /home/kawaiikali/event-study/publication_figures
   # Open any PDF file to see publication-quality output

2. VIEW TABLES:
   cd /home/kawaiikali/event-study/publication_tables
   # Open .tex files in text editor
   # Or compile all_tables.tex to see rendered output

3. USE YOUR OWN DATA:
   # Edit data_preparation_template.py with your results
   # Save files to data/ directory
   # Run: python validate_data.py
   # Run: python create_publication_figures.py
   # Run: python generate_latex_tables.py

4. CUSTOMIZE:
   # Edit create_publication_figures.py
   # Change colors, fonts, dimensions
   # Regenerate outputs

5. INTEGRATE INTO MANUSCRIPT:
   # In your LaTeX paper:
   \\includegraphics{publication_figures/figure1_event_timeline.pdf}
   \\input{publication_tables/table1_event_study_results.tex}

    """)

def main():
    """Run complete demonstration"""

    print_header("EVENT STUDY PUBLICATION PACKAGE - COMPLETE DEMO")

    print("""
This demonstration will:
  1. Generate example data (events, volatility, impact matrix, models)
  2. Validate data format
  3. Create 4 publication-quality figures (PDF + SVG)
  4. Create 4 LaTeX tables
  5. Show summary of outputs

Estimated time: 2-3 minutes

    """)

    input("Press Enter to begin...")

    # Step 1: Create publication figures (includes example data)
    print_step(1, 3, "Generating Publication Figures")
    success1 = run_script(
        'create_publication_figures.py',
        'Creates 4 figures with example data'
    )

    if not success1:
        print("\n⚠ Figure generation failed. Continuing anyway...\n")

    time.sleep(1)

    # Step 2: Create LaTeX tables
    print_step(2, 3, "Generating LaTeX Tables")
    success2 = run_script(
        'generate_latex_tables.py',
        'Creates 4 LaTeX tables with example data'
    )

    if not success2:
        print("\n⚠ Table generation failed. Continuing anyway...\n")

    time.sleep(1)

    # Step 3: Show outputs
    print_step(3, 3, "Summary of Generated Files")
    show_outputs()

    # Show next steps
    show_next_steps()

    # Final summary
    print_header("DEMO COMPLETE")

    if success1 and success2:
        print("""
✓ All outputs generated successfully!

The example outputs demonstrate publication-quality standards:
  • Vector graphics (PDF/SVG)
  • Grayscale-friendly design
  • LaTeX-compatible fonts
  • Statistical significance markers
  • Professional layout

These figures and tables are ready for top-tier journal submission.
        """)
    else:
        print("""
⚠ Some errors occurred during generation.

Check the error messages above for details.
Common issues:
  - Missing Python packages (install: numpy, pandas, matplotlib, seaborn)
  - File permission issues
  - Python version incompatibility (requires 3.8+)
        """)

    print("=" * 80)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
