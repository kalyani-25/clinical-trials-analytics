"""
Project 5: Clinical Trials Analysis
Data from ClinicalTrials.gov (simulated for demo)
Run: python trials_analysis.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

np.random.seed(42)
n = 2400

phases = ['Phase I', 'Phase II', 'Phase III', 'Phase IV']
areas  = ['Oncology', 'Infectious Disease', 'Cardiology', 'Neurology', 'Other']
phase_success = {'Phase I': 0.65, 'Phase II': 0.40, 'Phase III': 0.28, 'Phase IV': 0.72}

df = pd.DataFrame({
    'nct_id':             [f'NCT{np.random.randint(10000000,99999999)}' for _ in range(n)],
    'phase':              np.random.choice(phases, n, p=[0.25,0.30,0.30,0.15]),
    'therapeutic_area':   np.random.choice(areas, n, p=[0.35,0.20,0.18,0.14,0.13]),
    'enrollment':         np.random.lognormal(5, 1.5, n).astype(int).clip(5),
    'duration_months':    np.random.randint(6, 120, n),
    'sponsor_type':       np.random.choice(['Industry','Academic','NIH'], n, p=[0.55,0.30,0.15]),
    'start_year':         np.random.randint(2005, 2023, n),
})

df['success'] = df.apply(lambda r: np.random.binomial(1, phase_success[r['phase']]), axis=1)
df['status']  = df.apply(lambda r: 'Completed-Success' if r['success'] else
                         np.random.choice(['Completed-Failed','Terminated','Withdrawn'], p=[0.55,0.30,0.15]), axis=1)

df.to_csv('clinical_trials.csv', index=False)
print(f"Saved clinical_trials.csv ({len(df):,} trials)")
print("\nSuccess rates by phase:")
print(df.groupby('phase')['success'].mean().reindex(phases).round(3) * 100)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Clinical Trials Meta-Analysis Dashboard', fontsize=15, fontweight='bold')

phase_sr = df.groupby('phase')['success'].mean().reindex(phases) * 100
phase_colors = ['#1D9E75','#EF9F27','#E24B4A','#378ADD']
bars = axes[0,0].bar(phases, phase_sr.values, color=phase_colors)
axes[0,0].set_title('Success Rate by Phase (%)')
axes[0,0].set_ylabel('Success Rate %')
axes[0,0].set_ylim(0, 85)
for bar, val in zip(bars, phase_sr.values):
    axes[0,0].text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.0f}%', ha='center', fontsize=11, fontweight='bold')

area_counts = df['therapeutic_area'].value_counts()
area_colors = ['#E24B4A','#1D9E75','#378ADD','#7F77DD','#888780']
axes[0,1].pie(area_counts.values, labels=area_counts.index,
              colors=area_colors, autopct='%1.0f%%', startangle=90)
axes[0,1].set_title('Trials by Therapeutic Area')

phase_dur = df.groupby(['phase','sponsor_type'])['duration_months'].median().unstack()
phase_dur.plot(kind='bar', ax=axes[1,0], color=['#378ADD','#7F77DD','#1D9E75'], rot=20)
axes[1,0].set_title('Median Trial Duration by Phase & Sponsor Type')
axes[1,0].set_ylabel('Months')
axes[1,0].legend(title='Sponsor', fontsize=9)
axes[1,0].set_xlabel('')

for area, color in zip(areas[:3], ['#E24B4A','#378ADD','#1D9E75']):
    sub = df[df['therapeutic_area'] == area]['enrollment']
    axes[1,1].hist(np.log10(sub.clip(10)), bins=20, alpha=0.5, label=area, color=color)
axes[1,1].set_title('Enrollment Distribution by Therapeutic Area')
axes[1,1].set_xlabel('log10(Enrollment)')
axes[1,1].set_ylabel('Number of Trials')
axes[1,1].legend(fontsize=9)
axes[1,1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('trials_analysis.png', dpi=150, bbox_inches='tight')
print("Saved trials_analysis.png")
