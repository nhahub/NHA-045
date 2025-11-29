"""
train_classifier.py - Engagement Classifier Training
====================================================

Trains multiple ML classifiers and saves the best one in a format
compatible with app.py.

Classifiers tested:
- Random Forest
- XGBoost
- Support Vector Machine (SVM)

Output format (compatible with app.py):
{
    'model': trained_model,
    'scaler': StandardScaler(),
    'feature_names': [...],
    'model_type': 'RandomForest',
    'val_accuracy': 0.XX
}
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Try to import xgboost
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not available, skipping...")

def load_data(data_path='training_data.csv'):
    """Load training data."""
    df = pd.read_csv(Path(__file__).parent / data_path)
    
    # Separate features and labels
    X = df.drop('engagement_level', axis=1)
    y = df['engagement_level']
    
    # Map labels to 0-3 for sklearn (will reverse later)
    # 1 (Highly Engaged) -> 3
    # 2 (Engaged) -> 2
    # 3 (Partially Engaged) -> 1
    # 4 (Disengaged) -> 0
    label_map = {1: 3, 2: 2, 3: 1, 4: 0}
    y = y.map(label_map)
    
    return X, y

def train_model(model_name, model, X_train, X_test, y_train, y_test, param_grid=None):
    """Train and evaluate a single model."""
    print(f"\n{'='*60}")
    print(f"Training {model_name}...")
    print(f"{'='*60}")
    
    if param_grid:
        print("Performing GridSearchCV...")
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")
    else:
        model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print(f"{model_name} Results:")
    print(f"{'='*60}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['Disengaged', 'Partially Engaged', 'Engaged', 'Highly Engaged']))
    
    return model, accuracy

def main():
    """Main training pipeline."""
    print("🚀 Starting Engagement Classifier Training Pipeline\n")
    
    # 1. Load data
    print("📊 Loading training data...")
    X, y = load_data()
    print(f"   Dataset shape: {X.shape}")
    print(f"   Features: {list(X.columns)}")
    print(f"   Class distribution:\n{y.value_counts().sort_index()}\n")
    
    # 2. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✅ Train/Test split: {len(X_train)}/{len(X_test)}")
    
    # 3. Scale features
    print("\n🔧 Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train models
    models = {}
    results = {}
    
    # Random Forest
    rf_params = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5]
    }
    rf_model, rf_acc = train_model(
        "Random Forest",
        RandomForestClassifier(random_state=42),
        X_train_scaled, X_test_scaled, y_train, y_test,
        param_grid=rf_params
    )
    models['RandomForest'] = rf_model
    results['RandomForest'] = rf_acc
    
    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_params = {
            'n_estimators': [100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1]
        }
        xgb_model, xgb_acc = train_model(
            "XGBoost",
            XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
            X_train_scaled, X_test_scaled, y_train, y_test,
            param_grid=xgb_params
        )
        models['XGBoost'] = xgb_model
        results['XGBoost'] = xgb_acc
    
    # SVM
    svm_params = {
        'C': [0.1, 1, 10],
        'kernel': ['rbf', 'linear']
    }
    svm_model, svm_acc = train_model(
        "SVM",
        SVC(random_state=42, probability=True),
        X_train_scaled, X_test_scaled, y_train, y_test,
        param_grid=svm_params
    )
    models['SVM'] = svm_model
    results['SVM'] = svm_acc
    
    # 5. Select best model
    print(f"\n{'='*60}")
    print("📊 Model Comparison:")
    print(f"{'='*60}")
    for name, acc in results.items():
        print(f"{name:20s}: {acc:.4f}")
    
    best_model_name = max(results, key=results.get)
    best_model = models[best_model_name]
    best_accuracy = results[best_model_name]
    
    print(f"\n🏆 Best Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
    
    # 6. Save model in app.py compatible format
    output = {
        'model': best_model,
        'scaler': scaler,
        'feature_names': list(X.columns),
        'model_type': best_model_name,
        'val_accuracy': best_accuracy
    }
    
    output_dir = Path(__file__).parent.parent / 'weights'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / 'engagement_classifier.pkl'
    
    joblib.dump(output, output_path)
    print(f"\n✅ Model saved to: {output_path}")
    print("\n🎉 Training complete!")
    
    return output

if __name__ == "__main__":
    model = main()
