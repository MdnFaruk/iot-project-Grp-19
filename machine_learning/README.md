# IoT ML — EverywhereML demo

This repo demonstrates training a small classification model with EverywhereML and exporting it for edge use (MicroPython/embedded). It includes example scripts and a dataset.

**Files**
- `training_data.csv`: example collected sensor records (temperature, humidity, pressure, status).
- `train_model.py`: trains a classifier on data and attempts to export it for MicroPython.
- `comfort_model.py`: generated model code (created when export succeeds).
- `plot.py`: analyzing the training data graph.

**Prerequisites**
- Python 3.8+ (venv is recommended)
- Install dependencies:

```bash
pip install -r requirements.txt
or
pip install everywhereml scikit-learn pandas numpy
```

- Model training and export: `train_model.py` trains a scikit-learn compatible classifier via the EverywhereML wrappers (e.g., `everywhereml.sklearn.tree.DecisionTreeClassifier` or `everywhereml.sklearn.ensemble.RandomForestClassifier`). The script will attempt multiple export methods (for MicroPython or Python) and save the first successful export as `comfort_model.py`.

**Notes and tips**
- Decision trees typically export to compact MicroPython-friendly code; RandomForest may not provide direct `port`/`to_micropython` methods in some EverywhereML versions — if export fails, try using a `DecisionTreeClassifier` (change the import in `train_model.py`).

- To generate a `Dataset` from data frame (used by EverywhereML preprocessors):

```python
from everywhereml.data.Dataset import Dataset
dataset = Dataset.from_XY(X, y, feature_names=['temperature','humidity','pressure'], target_names=['Uncomfortable','Comfortable'])
```

- Train and export a model:

```bash
python ./train_model.py
```

Expected: prints training progress, accuracy, and either a successful export message and `comfort_model.py` created or diagnostic messages explaining why export failed.

**Deploying to a Pico (MicroPython)**
1. Open `comfort_model.py` in Thonny.
2. Upload the file and any helper code to Pico.
3. Call `predict([temp, humidity, pressure])` or the exported function as indicated in the generated file.

---