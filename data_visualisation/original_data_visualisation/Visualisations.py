import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = r'C:\Master\an_2_sem_1\Big_Data\heart_dataset.csv'
output_dir = r'C:\Master\an_2_sem_1\Big_Data'

heart_data = pd.read_csv(file_path)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sns.set(style="whitegrid")

columns_to_plot = ['age', 'chol', 'trestbps', 'thalach', 'oldpeak']
for col in columns_to_plot:
    plt.figure()
    sns.histplot(heart_data[col], kde=True, bins=30, color='blue')
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'{col}_distribution.png'))
    plt.close()

categorical_columns = ['sex', 'cp', 'fbs', 'restecg', 'slope', 'ca', 'thal']
for col in categorical_columns:
    plt.figure()
    sns.countplot(data=heart_data, x=col, palette='viridis')
    plt.title(f'Count of {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, f'{col}_count.png'))
    plt.close()

plt.figure(figsize=(10, 8))
correlation_matrix = heart_data.corr()
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm")
plt.title('Correlation Heatmap')
plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
plt.close()

plt.figure()
sns.countplot(data=heart_data, x='output', palette='Set2')
plt.title('Heart Disease Presence')
plt.xlabel('Heart Disease (1 = Yes, 0 = No)')
plt.ylabel('Count')
plt.savefig(os.path.join(output_dir, 'heart_disease_distribution.png'))
plt.close()

plt.figure()
sns.boxplot(data=heart_data, x='output', y='age', palette='Set3')
plt.title('Age vs Heart Disease')
plt.xlabel('Heart Disease (1 = Yes, 0 = No)')
plt.ylabel('Age')
plt.savefig(os.path.join(output_dir, 'age_vs_heart_disease.png'))
plt.close()

plt.figure()
sns.scatterplot(data=heart_data, x='thalach', y='oldpeak', hue='exang', style='output', palette='coolwarm')
plt.title('Max Heart Rate vs Oldpeak by Exercise Angina')
plt.xlabel('Max Heart Rate Achieved')
plt.ylabel('ST Depression (Oldpeak)')
plt.savefig(os.path.join(output_dir, 'exercise_induced_effects.png'))
plt.close()

plt.figure()
sns.countplot(data=heart_data, x='cp', hue='output', palette='muted')
plt.title('Chest Pain Type vs Heart Disease')
plt.xlabel('Chest Pain Type')
plt.ylabel('Count')
plt.savefig(os.path.join(output_dir, 'chest_pain_analysis.png'))
plt.close()

from pandas.plotting import parallel_coordinates

plt.figure(figsize=(12, 6))
subset = heart_data[['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'output']]
parallel_coordinates(subset, class_column='output', colormap='viridis')
plt.title('Parallel Coordinates Plot')
plt.savefig(os.path.join(output_dir, 'parallel_coordinates.png'))
plt.close()

print(f"All visualizations saved in {output_dir}")
