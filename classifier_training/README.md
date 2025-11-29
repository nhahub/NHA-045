# ML Classifier Training Pipeline

This folder contains the complete pipeline for training an engagement classification model that can be used with the SEMSOL app.

## 📁 Files

- **`generate_training_data.py`**: Generates synthetic training data with realistic engagement patterns
- **`train_classifier.py`**: Trains multiple classifiers (Random Forest, XGBoost, SVM) and saves the best one
- **`evaluate_model.py`**: Evaluates the trained model and generates visualizations
- **`requirements.txt`**: Python dependencies for training

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd classifier_training
pip install -r requirements.txt
```

### 2. Generate Training Data

```bash
python generate_training_data.py
```

This creates `training_data.csv` with 4,000 samples (1,000 per engagement class).

### 3. Train the Model

```bash
python train_classifier.py
```

This will:
- Train Random Forest, XGBoost, and SVM classifiers
- Perform hyperparameter tuning with cross-validation
- Save the best model to `../weights/engagement_classifier.pkl`

Expected output:
```
🏆 Best Model: RandomForest (Accuracy: 0.9X)
✅ Model saved to: ../weights/engagement_classifier.pkl
```

### 4. Evaluate the Model

```bash
python evaluate_model.py
```

Generates:
- `confusion_matrix.png`: Confusion matrix visualization
- `feature_importance.png`: Top features plot
- Console output with detailed classification metrics

## 📊 Model Output Format

The saved model (`.pkl` file) contains:

```python
{
    'model': trained_model,           # Trained sklearn/xgboost model
    'scaler': StandardScaler(),       # Feature scaler
    'feature_names': [...],           # List of 19 feature names
    'model_type': 'RandomForest',     # Algorithm name
    'val_accuracy': 0.XX              # Validation accuracy
}
```

This format is compatible with `app.py` and `app_deploy.py`.

## 🎯 Features (19 total)

The model uses these features extracted from gaze and blink data:

**Gaze (Pitch/Yaw):**
- mean, std, min, max, p25, p50, p75 (7 features each)

**Eye Aspect Ratio (EAR):**
- mean, std, min, max, p25, p50, p75 (7 features)

**Blink Metrics:**
- blink_count, blink_rate (2 features)

**Attention:**
- face_ratio, pitch_stab, yaw_stab (3 features)

## 📈 Engagement Levels

- **1 - Highly Engaged**: Attentive, stable gaze, normal blink rate
- **2 - Engaged**: Generally attentive with minor variations
- **3 - Partially Engaged**: Distracted, irregular patterns
- **4 - Disengaged**: Looking away, drowsy, or not paying attention

## 🔄 Using with the App

After training, the model is automatically saved to the correct location:

```bash
gaze-estimation/weights/engagement_classifier.pkl
```

The app will automatically use it when you enable "Use ML Classifier" in the sidebar.

## ⚠️ Important Notes

- **Synthetic Data**: The current model uses synthetic data for demonstration. For production, collect and label real engagement data.
- **Retraining**: To retrain with new data, replace `training_data.csv` and run `train_classifier.py` again.
- **Custom Features**: If you modify the feature set, update both the data generator and the app's `extract_features_for_ml()` function.

## 🛠️ Customization

### Add More Training Data

Edit `generate_training_data.py` and adjust:

```python
df = generate_dataset(n_samples_per_class=2000)  # Increase from 1000
```

### Try Different Algorithms

Edit `train_classifier.py` to add more models or adjust hyperparameters.

### Change Engagement Patterns

Edit `ENGAGEMENT_PATTERNS` in `generate_training_data.py` to match your specific use case.

---

**Questions?** Check the main project README or the SEMSOL documentation.
