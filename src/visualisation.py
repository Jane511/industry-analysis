"""Professional visualisation functions for the industry risk analysis pipeline."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------
RISK_COLOURS = {
    'Low': '#2e7d32',
    'Medium': '#f9a825',
    'Elevated': '#e65100',
    'High': '#b71c1c',
}

SCORE_CMAP = mcolors.LinearSegmentedColormap.from_list(
    'risk', ['#2e7d32', '#a5d6a7', '#fff9c4', '#ffcc80', '#ef9a9a', '#b71c1c'], N=256
)

FIG_DPI = 180
FONT_TITLE = 13
FONT_LABEL = 11
FONT_TICK = 9
FONT_ANNOT = 8


def _apply_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
    })


def _risk_colour(score: float) -> str:
    if score <= 2.0:
        return RISK_COLOURS['Low']
    if score <= 3.0:
        return RISK_COLOURS['Medium']
    if score <= 4.0:
        return RISK_COLOURS['Elevated']
    return RISK_COLOURS['High']


# ---------------------------------------------------------------------------
# 1. Risk heatmap — industries x risk dimensions
# ---------------------------------------------------------------------------
def plot_risk_heatmap(macro_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    cols = ['cyclical_score', 'rate_sensitivity_score', 'demand_dependency_score',
            'external_shock_score', 'macro_risk_score']
    labels = ['Cyclicality', 'Rate\nSensitivity', 'Demand\nDependency',
              'External\nShock', 'Macro\nComposite']

    available = [c for c in cols if c in macro_df.columns]
    if not available:
        return

    df = macro_df.sort_values('industry_base_risk_score', ascending=True).copy()
    matrix = df[available].values.astype(float)
    industries = df['industry'].values

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(matrix, cmap=SCORE_CMAP, aspect='auto', vmin=1, vmax=5)

    ax.set_xticks(range(len(available)))
    ax.set_xticklabels([labels[cols.index(c)] for c in available],
                       fontsize=FONT_TICK, ha='center')
    ax.set_yticks(range(len(industries)))
    ax.set_yticklabels(industries, fontsize=FONT_TICK)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            if np.isnan(val):
                continue
            colour = 'white' if val >= 3.5 else 'black'
            ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                    fontsize=FONT_ANNOT, fontweight='bold', color=colour)

    cbar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('Risk Score (1=Low, 5=High)', fontsize=FONT_TICK)

    ax.set_title('Industry Risk Dimensions Heatmap', fontsize=FONT_TITLE, fontweight='bold', pad=12)
    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Risk bar chart — colour-coded by risk band
# ---------------------------------------------------------------------------
def plot_risk_bar_chart(macro_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    df = macro_df[['industry', 'industry_base_risk_score']].sort_values(
        'industry_base_risk_score', ascending=True).copy()
    colours = [_risk_colour(s) for s in df['industry_base_risk_score']]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df['industry'], df['industry_base_risk_score'], color=colours, edgecolor='white', height=0.65)

    for bar, score in zip(bars, df['industry_base_risk_score']):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{score:.2f}', va='center', fontsize=FONT_ANNOT, fontweight='bold')

    ax.set_xlim(0, 5.2)
    ax.set_xlabel('Industry Base Risk Score (1=Low, 5=High)', fontsize=FONT_LABEL)
    ax.set_title('Industry Base Risk Score by Sector', fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.tick_params(axis='y', labelsize=FONT_TICK)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=l) for l, c in RISK_COLOURS.items()]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=FONT_TICK, title='Risk Band', title_fontsize=FONT_TICK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Employment growth — colour-coded by direction
# ---------------------------------------------------------------------------
def plot_employment_growth(macro_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    df = macro_df[['industry', 'employment_yoy_growth_pct']].dropna().sort_values(
        'employment_yoy_growth_pct', ascending=True).copy()
    colours = ['#c62828' if v < 0 else '#2e7d32' for v in df['employment_yoy_growth_pct']]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df['industry'], df['employment_yoy_growth_pct'], color=colours, edgecolor='white', height=0.65)

    for bar, val in zip(bars, df['employment_yoy_growth_pct']):
        offset = 0.3 if val >= 0 else -0.3
        ha = 'left' if val >= 0 else 'right'
        ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
                f'{val:+.1f}%', va='center', ha=ha, fontsize=FONT_ANNOT, fontweight='bold')

    ax.axvline(0, color='grey', linewidth=0.8)
    ax.set_xlabel('Employment Growth YoY (%)', fontsize=FONT_LABEL)
    ax.set_title('Employment Growth by Industry (Trend Series)', fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.tick_params(axis='y', labelsize=FONT_TICK)
    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Radar / spider chart — borrower vs benchmark
# ---------------------------------------------------------------------------
def plot_radar_chart(borrower_df: pd.DataFrame, borrower_name: str, output_path: Path) -> None:
    _apply_style()

    score_cols = ['ebitda_margin_score', 'debt_to_ebitda_score', 'icr_score',
                  'ar_days_score', 'ap_days_score', 'inventory_days_score']
    labels = ['EBITDA\nMargin', 'Debt /\nEBITDA', 'Interest\nCoverage',
              'AR\nDays', 'AP\nDays', 'Inventory\nDays']

    row = borrower_df[borrower_df['borrower_name'] == borrower_name]
    if row.empty:
        return
    row = row.iloc[0]
    values = [float(row[c]) if pd.notna(row[c]) else 3 for c in score_cols]

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += [angles[0]]
    benchmark = [3] * (N + 1)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles, values_plot, 'o-', linewidth=2, color='#1565c0', label=borrower_name)
    ax.fill(angles, values_plot, alpha=0.15, color='#1565c0')
    ax.plot(angles, benchmark, '--', linewidth=1.5, color='grey', alpha=0.7, label='Benchmark (3.0)')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=FONT_TICK)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=7)

    ax.set_title(f'{borrower_name}\nBottom-Up Risk Profile',
                 fontsize=FONT_TITLE, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=FONT_TICK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Score waterfall — component breakdown
# ---------------------------------------------------------------------------
def plot_score_waterfall(row: pd.Series, output_path: Path) -> None:
    _apply_style()

    components = [
        ('Classification\n(35%)', float(row['classification_risk_score']) * 0.35),
        ('Macro\n(30%)', float(row['macro_risk_score']) * 0.30),
        ('Bottom-Up\n(35%)', float(row['bottom_up_risk_score']) * 0.35),
    ]

    labels = [c[0] for c in components]
    values = [c[1] for c in components]
    total = sum(values)
    colours = ['#1565c0', '#00838f', '#6a1b9a']

    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = 0
    for i, (label, val) in enumerate(components):
        ax.bar('Score\nBreakdown', val, bottom=bottom, color=colours[i],
               edgecolor='white', width=0.5, label=f'{label}: {val:.2f}')
        ax.text(0, bottom + val / 2, f'{val:.2f}', ha='center', va='center',
                fontsize=FONT_LABEL, fontweight='bold', color='white')
        bottom += val

    ax.axhline(total, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax.text(0.35, total + 0.08, f'Final: {total:.2f}', fontsize=FONT_LABEL, fontweight='bold')

    ax.set_ylim(0, max(5, total + 0.5))
    ax.set_ylabel('Risk Score Contribution', fontsize=FONT_LABEL)
    borrower_name = row.get('borrower_name', 'Borrower')
    ax.set_title(f'{borrower_name} — Score Composition',
                 fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.legend(loc='upper right', fontsize=FONT_TICK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Borrower scorecard — colour-coded bar chart
# ---------------------------------------------------------------------------
def plot_borrower_scorecard(scorecard_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    df = scorecard_df.sort_values('final_industry_risk_score', ascending=True).copy()
    colours = [_risk_colour(s) for s in df['final_industry_risk_score']]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df['borrower_name'], df['final_industry_risk_score'],
                   color=colours, edgecolor='white', height=0.55)

    for bar, score, level in zip(bars, df['final_industry_risk_score'], df['risk_level']):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{score:.2f}  ({level})', va='center', fontsize=FONT_ANNOT, fontweight='bold')

    ax.set_xlim(0, 5.2)
    ax.set_xlabel('Final Industry Risk Score', fontsize=FONT_LABEL)
    ax.set_title('Borrower Industry Risk Scorecard', fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.tick_params(axis='y', labelsize=FONT_TICK)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=l) for l, c in RISK_COLOURS.items()]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=FONT_TICK,
              title='Risk Band', title_fontsize=FONT_TICK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. Pricing grid — base rate + industry loading
# ---------------------------------------------------------------------------
def plot_pricing_grid(pricing_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    df = pricing_df.sort_values('indicative_rate_pct', ascending=True).copy()
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.barh(df['borrower_name'], df['base_margin_pct'], color='#90a4ae',
            edgecolor='white', height=0.55, label='Base margin')
    ax.barh(df['borrower_name'], df['industry_loading_pct'],
            left=df['base_margin_pct'], color=[_risk_colour(s) for s in df['final_industry_risk_score']],
            edgecolor='white', height=0.55, label='Industry risk loading')

    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row['indicative_rate_pct'] + 0.05, i,
                f'{row["indicative_rate_pct"]:.2f}%', va='center',
                fontsize=FONT_ANNOT, fontweight='bold')

    ax.set_xlabel('Indicative Rate Above Cash Rate (%)', fontsize=FONT_LABEL)
    ax.set_title('Indicative Pricing by Borrower (Cash Rate + Margin + Industry Loading)',
                 fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.tick_params(axis='y', labelsize=FONT_TICK)
    ax.legend(fontsize=FONT_TICK, loc='lower right')

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. Concentration dashboard — current exposure vs limit
# ---------------------------------------------------------------------------
def plot_concentration_dashboard(conc_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    df = conc_df.sort_values('concentration_limit_pct', ascending=False).copy()
    x = np.arange(len(df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_limit = ax.bar(x - width / 2, df['concentration_limit_pct'], width,
                        label='Limit', color='#b0bec5', edgecolor='white')
    bar_colours = ['#c62828' if row['breach'] else '#2e7d32'
                   for _, row in df.iterrows()]
    bars_actual = ax.bar(x + width / 2, df['current_exposure_pct'], width,
                         label='Current Exposure', color=bar_colours, edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(df['industry'], rotation=35, ha='right', fontsize=FONT_TICK)
    ax.set_ylabel('Portfolio Share (%)', fontsize=FONT_LABEL)
    ax.set_title('Sector Concentration: Current Exposure vs Limit',
                 fontsize=FONT_TITLE, fontweight='bold', pad=12)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#b0bec5', label='Limit'),
        Patch(facecolor='#2e7d32', label='Within limit'),
        Patch(facecolor='#c62828', label='Breach'),
    ]
    ax.legend(handles=legend_elements, fontsize=FONT_TICK)

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 9. Watchlist summary
# ---------------------------------------------------------------------------
def plot_watchlist_summary(watchlist_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    if watchlist_df.empty:
        return

    trigger_counts = watchlist_df.groupby('industry').size().sort_values(ascending=True)
    colours = ['#c62828' if c >= 3 else '#e65100' if c >= 2 else '#f9a825'
               for c in trigger_counts.values]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(trigger_counts.index, trigger_counts.values, color=colours,
                   edgecolor='white', height=0.55)

    for bar, count in zip(bars, trigger_counts.values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f'{count} trigger{"s" if count > 1 else ""}',
                va='center', fontsize=FONT_ANNOT, fontweight='bold')

    ax.set_xlabel('Number of Watchlist Triggers', fontsize=FONT_LABEL)
    ax.set_title('Industry Watchlist — Trigger Count by Sector',
                 fontsize=FONT_TITLE, fontweight='bold', pad=12)
    ax.tick_params(axis='y', labelsize=FONT_TICK)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)


# ---------------------------------------------------------------------------
# 10. Stress test impact — worst stressed score by industry
# ---------------------------------------------------------------------------
def plot_stress_test_impact(stress_df: pd.DataFrame, output_path: Path) -> None:
    _apply_style()

    if stress_df.empty:
        return

    df = (
        stress_df.groupby('industry', as_index=False)
        .agg(
            base_industry_risk_score=('base_industry_risk_score', 'max'),
            stressed_industry_risk_score=('stressed_industry_risk_score', 'max'),
            stress_delta=('stress_delta', 'max'),
        )
        .sort_values('stressed_industry_risk_score', ascending=True)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(df))
    ax.barh(y, df['base_industry_risk_score'], color='#b0bec5', edgecolor='white', height=0.6, label='Base score')
    ax.barh(
        y,
        df['stress_delta'],
        left=df['base_industry_risk_score'],
        color='#e65100',
        edgecolor='white',
        height=0.6,
        label='Stress uplift',
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df['industry'], fontsize=FONT_TICK)
    ax.set_xlabel('Industry Risk Score', fontsize=FONT_LABEL)
    ax.set_title('Industry Stress Test Impact (Worst Scenario by Sector)', fontsize=FONT_TITLE, fontweight='bold', pad=12)

    for idx, row in enumerate(df.itertuples(index=False)):
        ax.text(
            row.stressed_industry_risk_score + 0.04,
            idx,
            f'{row.stressed_industry_risk_score:.2f}',
            va='center',
            fontsize=FONT_ANNOT,
            fontweight='bold',
        )

    ax.legend(fontsize=FONT_TICK, loc='lower right')
    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
