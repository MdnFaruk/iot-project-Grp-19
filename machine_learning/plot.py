import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv("training_data.csv")

# Split data by class
comfortable = data[data['status'] == 'Comfortable']
uncomfortable = data[data['status'] == 'Uncomfortable']

# Plot histograms for each feature by class
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for i, col in enumerate(['temperature', 'humidity', 'pressure']):
    axes[i].hist(comfortable[col], bins=10, alpha=0.7,
                 label='Comfortable', color='green')
    axes[i].hist(uncomfortable[col], bins=10, alpha=0.7,
                 label='Uncomfortable', color='red')
    axes[i].set_title(f'{col.capitalize()} Distribution')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Frequency')
    axes[i].legend()

plt.tight_layout()
plt.savefig("feature_distributions.png", dpi=150)
plt.show()
