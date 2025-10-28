"""
LaTeX Table Generator for Event Study Results
==============================================

Generates publication-ready LaTeX tables for:
- Event study regression results
- Descriptive statistics
- Volatility model comparisons
- Robustness checks

Output format compatible with Journal of Finance, JFE, RFS style guides.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from code.core import config

OUTPUT_DIR = config.PUBLICATION_DIR / 'latex'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def format_coef_se(coef, se, pval):
    """
    Format coefficient with standard error and significance stars

    Parameters:
    -----------
    coef : float
        Coefficient estimate
    se : float
        Standard error
    pval : float
        P-value

    Returns:
    --------
    tuple : (formatted coefficient, formatted standard error)
    """
    # Determine significance stars
    if pval < 0.01:
        stars = '^{***}'
    elif pval < 0.05:
        stars = '^{**}'
    elif pval < 0.10:
        stars = '^{*}'
    else:
        stars = ''

    # Format numbers
    coef_str = f"{coef:.4f}{stars}"
    se_str = f"({se:.4f})"

    return coef_str, se_str

def generate_event_study_table(results_df):
    """
    Generate LaTeX table for event study regression results

    Parameters:
    -----------
    results_df : pd.DataFrame
        Columns: ['event_name', 'car', 'se', 'pval', 'event_type']
    """
    output_file = OUTPUT_DIR / 'table1_event_study_results.tex'

    # Separate by event type
    infra = results_df[results_df['event_type'] == 'infrastructure'].copy()
    reg = results_df[results_df['event_type'] == 'regulatory'].copy()

    latex = []
    latex.append(r"\begin{table}[htbp]")
    latex.append(r"  \centering")
    latex.append(r"  \caption{Event Study Results: Cumulative Abnormal Returns}")
    latex.append(r"  \label{tab:event_study}")
    latex.append(r"  \begin{tabular}{lcccc}")
    latex.append(r"    \toprule")
    latex.append(r"    Event & CAR & t-stat & N & Event Type \\")
    latex.append(r"    \midrule")
    latex.append(r"    \multicolumn{5}{l}{\textit{Panel A: Infrastructure Events}} \\")

    for _, row in infra.iterrows():
        t_stat = row['car'] / row['se']
        coef, se = format_coef_se(row['car'], row['se'], row['pval'])
        latex.append(f"    {row['event_name']} & {coef} & {t_stat:.2f} & {row.get('n_obs', 'N/A')} & Infrastructure \\\\")

    latex.append(r"    \midrule")
    latex.append(r"    \multicolumn{5}{l}{\textit{Panel B: Regulatory Events}} \\")

    for _, row in reg.iterrows():
        t_stat = row['car'] / row['se']
        coef, se = format_coef_se(row['car'], row['se'], row['pval'])
        latex.append(f"    {row['event_name']} & {coef} & {t_stat:.2f} & {row.get('n_obs', 'N/A')} & Regulatory \\\\")

    latex.append(r"    \bottomrule")
    latex.append(r"  \end{tabular}")
    latex.append(r"  \begin{tablenotes}")
    latex.append(r"    \small")
    latex.append(r"    \item \textit{Notes:} This table reports cumulative abnormal returns (CAR) over the event window [0, +5].")
    latex.append(r"    Standard errors are calculated using the market model with robust adjustment.")
    latex.append(r"    Statistical significance: *** p<0.01, ** p<0.05, * p<0.10.")
    latex.append(r"  \end{tablenotes}")
    latex.append(r"\end{table}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(latex))

    print(f"✓ Generated: {output_file}")
    return output_file

def generate_descriptive_stats_table(data_df):
    """
    Generate LaTeX table for descriptive statistics

    Parameters:
    -----------
    data_df : pd.DataFrame
        Cryptocurrency returns data (columns = crypto tickers)
    """
    output_file = OUTPUT_DIR / 'table2_descriptive_statistics.tex'

    # Calculate statistics
    stats = pd.DataFrame({
        'Mean': data_df.mean() * 100,  # Convert to %
        'Std Dev': data_df.std() * 100,
        'Min': data_df.min() * 100,
        'Max': data_df.max() * 100,
        'Skewness': data_df.skew(),
        'Kurtosis': data_df.kurtosis(),
        'N': data_df.count()
    })

    latex = []
    latex.append(r"\begin{table}[htbp]")
    latex.append(r"  \centering")
    latex.append(r"  \caption{Descriptive Statistics of Cryptocurrency Returns}")
    latex.append(r"  \label{tab:descriptive}")
    latex.append(r"  \begin{tabular}{lccccccc}")
    latex.append(r"    \toprule")
    latex.append(r"    Cryptocurrency & Mean & Std Dev & Min & Max & Skewness & Kurtosis & N \\")
    latex.append(r"    & (\%) & (\%) & (\%) & (\%) & & & \\")
    latex.append(r"    \midrule")

    for ticker, row in stats.iterrows():
        latex.append(
            f"    {ticker} & "
            f"{row['Mean']:.3f} & "
            f"{row['Std Dev']:.3f} & "
            f"{row['Min']:.3f} & "
            f"{row['Max']:.3f} & "
            f"{row['Skewness']:.3f} & "
            f"{row['Kurtosis']:.3f} & "
            f"{int(row['N'])} \\\\"
        )

    latex.append(r"    \bottomrule")
    latex.append(r"  \end{tabular}")
    latex.append(r"  \begin{tablenotes}")
    latex.append(r"    \small")
    latex.append(r"    \item \textit{Notes:} This table presents summary statistics for daily returns of major cryptocurrencies.")
    latex.append(r"    Returns are expressed in percentage terms. Sample period: [Insert dates here].")
    latex.append(r"  \end{tablenotes}")
    latex.append(r"\end{table}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(latex))

    print(f"✓ Generated: {output_file}")
    return output_file

def generate_volatility_model_table(model_results):
    """
    Generate LaTeX table comparing volatility models

    Parameters:
    -----------
    model_results : pd.DataFrame
        Columns: ['model_name', 'alpha', 'beta', 'gamma', 'aic', 'bic', 'log_likelihood']
    """
    output_file = OUTPUT_DIR / 'table3_volatility_models.tex'

    latex = []
    latex.append(r"\begin{table}[htbp]")
    latex.append(r"  \centering")
    latex.append(r"  \caption{Volatility Model Estimation Results}")
    latex.append(r"  \label{tab:volatility}")
    latex.append(r"  \begin{tabular}{lcccccc}")
    latex.append(r"    \toprule")
    latex.append(r"    Model & $\alpha$ & $\beta$ & $\gamma$ & AIC & BIC & Log-Likelihood \\")
    latex.append(r"    \midrule")

    for _, row in model_results.iterrows():
        alpha_str = f"{row['alpha']:.4f}" if pd.notna(row.get('alpha')) else '--'
        beta_str = f"{row['beta']:.4f}" if pd.notna(row.get('beta')) else '--'
        gamma_str = f"{row['gamma']:.4f}" if pd.notna(row.get('gamma')) else '--'

        latex.append(
            f"    {row['model_name']} & "
            f"{alpha_str} & "
            f"{beta_str} & "
            f"{gamma_str} & "
            f"{row['aic']:.2f} & "
            f"{row['bic']:.2f} & "
            f"{row['log_likelihood']:.2f} \\\\"
        )

    # Highlight best model
    best_aic_idx = model_results['aic'].idxmin()
    best_model = model_results.loc[best_aic_idx, 'model_name']

    latex.append(r"    \midrule")
    latex.append(f"    \\multicolumn{{7}}{{l}}{{Best Model (AIC): {best_model}}} \\\\")
    latex.append(r"    \bottomrule")
    latex.append(r"  \end{tabular}")
    latex.append(r"  \begin{tablenotes}")
    latex.append(r"    \small")
    latex.append(r"    \item \textit{Notes:} This table compares alternative volatility models estimated on Bitcoin returns.")
    latex.append(r"    $\alpha$ is the ARCH coefficient, $\beta$ is the GARCH coefficient, $\gamma$ is the asymmetry parameter.")
    latex.append(r"    Lower AIC and BIC indicate better model fit.")
    latex.append(r"  \end{tablenotes}")
    latex.append(r"\end{table}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(latex))

    print(f"✓ Generated: {output_file}")
    return output_file

def generate_regression_table(regression_results):
    """
    Generate LaTeX table for cross-sectional regression results

    Parameters:
    -----------
    regression_results : dict
        Format: {
            'model1': {'coefs': {...}, 'se': {...}, 'pvals': {...}, 'r2': 0.45, 'n': 100},
            'model2': {...}
        }
    """
    output_file = OUTPUT_DIR / 'table4_regression_results.tex'

    # Extract variable names from first model
    first_model = list(regression_results.values())[0]
    variables = list(first_model['coefs'].keys())

    latex = []
    latex.append(r"\begin{table}[htbp]")
    latex.append(r"  \centering")
    latex.append(r"  \caption{Cross-Sectional Regression Results}")
    latex.append(r"  \label{tab:regression}")

    # Create column specification
    n_models = len(regression_results)
    col_spec = 'l' + 'c' * n_models
    latex.append(f"  \\begin{{tabular}}{{{col_spec}}}")
    latex.append(r"    \toprule")

    # Header row
    header = "    Variable & " + " & ".join(regression_results.keys()) + " \\\\"
    latex.append(header)
    latex.append(r"    \midrule")

    # Coefficient rows
    for var in variables:
        row_parts = [var]
        for model_name, model_data in regression_results.items():
            coef = model_data['coefs'][var]
            se = model_data['se'][var]
            pval = model_data['pvals'][var]
            coef_str, _ = format_coef_se(coef, se, pval)
            row_parts.append(coef_str)

        latex.append("    " + " & ".join(row_parts) + " \\\\")

        # Add standard errors in next row
        se_parts = [""]
        for model_name, model_data in regression_results.items():
            se = model_data['se'][var]
            se_parts.append(f"({se:.4f})")
        latex.append("    " + " & ".join(se_parts) + " \\\\")
        latex.append("")  # Blank line for readability

    # Model statistics
    latex.append(r"    \midrule")
    latex.append("    Observations & " + " & ".join([str(m['n']) for m in regression_results.values()]) + " \\\\")
    latex.append("    $R^2$ & " + " & ".join([f"{m['r2']:.3f}" for m in regression_results.values()]) + " \\\\")

    latex.append(r"    \bottomrule")
    latex.append(r"  \end{tabular}")
    latex.append(r"  \begin{tablenotes}")
    latex.append(r"    \small")
    latex.append(r"    \item \textit{Notes:} This table reports cross-sectional regression results.")
    latex.append(r"    Standard errors in parentheses. Statistical significance: *** p<0.01, ** p<0.05, * p<0.10.")
    latex.append(r"  \end{tablenotes}")
    latex.append(r"\end{table}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(latex))

    print(f"✓ Generated: {output_file}")
    return output_file

def generate_example_tables():
    """Generate example tables with synthetic data"""
    print("=" * 80)
    print("LATEX TABLE GENERATOR - EXAMPLE MODE")
    print("=" * 80)
    print()

    # Example 1: Event study results
    print("[1/4] Generating event study results table...")
    events_data = pd.DataFrame({
        'event_name': [
            'FTX Collapse', 'Ethereum Merge', 'SEC vs Ripple',
            'China Mining Ban', 'MiCA Regulation'
        ],
        'event_type': ['infrastructure', 'infrastructure', 'regulatory', 'regulatory', 'regulatory'],
        'car': [-0.087, 0.042, 0.065, -0.034, -0.021],
        'se': [0.012, 0.015, 0.018, 0.011, 0.014],
        'pval': [0.001, 0.005, 0.001, 0.002, 0.133],
        'n_obs': [350, 350, 350, 350, 350]
    })
    generate_event_study_table(events_data)

    # Example 2: Descriptive statistics
    print("[2/4] Generating descriptive statistics table...")
    # Simulate returns data
    np.random.seed(42)
    returns_data = pd.DataFrame({
        'BTC': np.random.normal(0.001, 0.03, 1000),
        'ETH': np.random.normal(0.0015, 0.04, 1000),
        'BNB': np.random.normal(0.002, 0.05, 1000),
    })
    generate_descriptive_stats_table(returns_data)

    # Example 3: Volatility models
    print("[3/4] Generating volatility model comparison table...")
    vol_models = pd.DataFrame({
        'model_name': ['GARCH(1,1)', 'EGARCH', 'GJR-GARCH'],
        'alpha': [0.0523, 0.1234, 0.0487],
        'beta': [0.9123, 0.8956, 0.9234],
        'gamma': [np.nan, -0.0234, 0.0345],
        'aic': [4398.67, 4405.23, 4392.15],
        'bic': [4429.54, 4436.01, 4422.93],
        'log_likelihood': [-2195.33, -2198.62, -2192.08]
    })
    generate_volatility_model_table(vol_models)

    # Example 4: Regression results
    print("[4/4] Generating regression results table...")
    regression_data = {
        'Model 1': {
            'coefs': {'Constant': 0.0123, 'Market Beta': 0.8456, 'Size': -0.0034},
            'se': {'Constant': 0.0045, 'Market Beta': 0.0234, 'Size': 0.0012},
            'pvals': {'Constant': 0.006, 'Market Beta': 0.001, 'Size': 0.005},
            'r2': 0.456,
            'n': 350
        },
        'Model 2': {
            'coefs': {'Constant': 0.0145, 'Market Beta': 0.8234, 'Size': -0.0029, 'Liquidity': 0.0156},
            'se': {'Constant': 0.0048, 'Market Beta': 0.0256, 'Size': 0.0013, 'Liquidity': 0.0067},
            'pvals': {'Constant': 0.003, 'Market Beta': 0.001, 'Size': 0.025, 'Liquidity': 0.020},
            'r2': 0.478,
            'n': 350
        }
    }
    generate_regression_table(regression_data)

    print()
    print("=" * 80)
    print("ALL TABLES GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print(f"Output directory: {OUTPUT_DIR}/")
    print()
    print("LaTeX tables ready to \\input{} into your manuscript.")
    print("Requires packages: booktabs, threeparttable")
    print()

def create_master_latex_file():
    """Create a master LaTeX file that includes all tables"""
    output_file = OUTPUT_DIR / 'all_tables.tex'

    latex = []
    latex.append(r"% Master file for all event study tables")
    latex.append(r"% Compile this to see all tables in one document")
    latex.append(r"")
    latex.append(r"\documentclass[12pt]{article}")
    latex.append(r"\usepackage{booktabs}")
    latex.append(r"\usepackage{threeparttable}")
    latex.append(r"\usepackage[margin=1in]{geometry}")
    latex.append(r"")
    latex.append(r"\begin{document}")
    latex.append(r"")
    latex.append(r"\section*{Event Study Tables}")
    latex.append(r"")
    latex.append(r"\input{table1_event_study_results.tex}")
    latex.append(r"\clearpage")
    latex.append(r"")
    latex.append(r"\input{table2_descriptive_statistics.tex}")
    latex.append(r"\clearpage")
    latex.append(r"")
    latex.append(r"\input{table3_volatility_models.tex}")
    latex.append(r"\clearpage")
    latex.append(r"")
    latex.append(r"\input{table4_regression_results.tex}")
    latex.append(r"")
    latex.append(r"\end{document}")

    with open(output_file, 'w') as f:
        f.write('\n'.join(latex))

    print(f"✓ Generated master file: {output_file}")
    print("  Compile with: pdflatex all_tables.tex")

if __name__ == '__main__':
    generate_example_tables()
    create_master_latex_file()
