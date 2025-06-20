```python
import os
os.makedirs("dashboard/plots", exist_ok=True)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
def plot_dynamics(df):
    
# ВИЗУАЛИЗАЦИЯ ДАННЫХ

df = pd.read_csv('winline_data_clean.csv', parse_dates=['timestamp'])

# Визуализация динамики коэффициентов
plt.figure(figsize=(14, 8))
top_matches = df.groupby(['team1', 'team2']).size().nlargest(3).index  # Топ-3 матча
filtered_df = df[df[['team1', 'team2']].apply(tuple, axis=1).isin(top_matches)]

# График для каждого из топ-матчей
for match in top_matches:
    match_data = filtered_df[(filtered_df['team1'] == match[0]) & (filtered_df['team2'] == match[1])]
    plt.plot(match_data['timestamp'], match_data['coeff_win1'], label=f'{match[0]} (П1)')
    plt.plot(match_data['timestamp'], match_data['coeff_win2'], label=f'{match[1]} (П2)')
    if 'coeff_draw' in match_data.columns:
        plt.plot(match_data['timestamp'], match_data['coeff_draw'], label='Ничья')

plt.title('Динамика коэффициентов для популярных матчей', fontsize=16)
plt.xlabel('Время', fontsize=12)
plt.ylabel('Коэффициент', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/dynamics.png")
plt.show(block=True)

# Визуализация распределения коэффициентов по видам спорта
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='sport', y='coeff_win1', showfliers=False, color='#1f77b4', width=0.4)
sns.boxplot(data=df, x='sport', y='coeff_win2', showfliers=False, color='#ff7f0e', width=0.4)

plt.title('Распределение коэффициентов по видам спорта', fontsize=16)
plt.xlabel('Вид спорта', fontsize=12)
plt.ylabel('Коэффициент', fontsize=12)
plt.legend(handles=[plt.Line2D([0], [0], color='#1f77b4', lw=4, label='Коэф. П1'),
                    plt.Line2D([0], [0], color='#ff7f0e', lw=4, label='Коэф. П2')],
           loc='upper right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("plots/boxplot.png")
plt.show(block=True)

# Облако слов для визуализации частоты упоминания команд
all_teams = pd.concat([df['team1'], df['team2']]).value_counts().to_dict()
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(all_teams)

plt.figure(figsize=(12, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Частота упоминания команд в матчах', fontsize=16)
plt.tight_layout()
plt.savefig("plots/wordcloud.png")
plt.show(block=True)

# Визуализация соотношения коэффициентов команд в матчах
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='coeff_win1', y='coeff_win2', hue='sport',
                palette='viridis', alpha=0.7, s=100)

plt.plot([1, max(df[['coeff_win1', 'coeff_win2']].max())],
         [1, max(df[['coeff_win1', 'coeff_win2']].max())],
         'r--', alpha=0.5)

plt.title('Соотношение коэффициентов команд в матчах', fontsize=16)
plt.xlabel('Коэффициент П1', fontsize=12)
plt.ylabel('Коэффициент П2', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(title='Вид спорта')
plt.tight_layout()
plt.savefig("plots/scatter.png")
plt.show(block=True)
```
