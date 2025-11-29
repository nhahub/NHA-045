"""
evaluate_model.py - Model Evaluation & Visualization
===================================================

Loads a trained classifier and generates evaluation metrics:
- Confusion matrix
- Feature importance
- Classification report
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

def load_model(model_path='../weights/engagement_classifier.pkl'):
    """Load trained model."""
    model_data = joblib.load(Path(__file__).parent / model_path)
    return model_data

def evaluate_model(model_data, X_test, y_test):
    """Generate evaluation metrics."""
    model = model_data['model']
    scaler = model_data['scaler']
    
    # Scale test data
    X_test_scaled = scaler.transform(X_test)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    
    # Classification report
    print("\n" + "="*60)
    print("Classification Report:")
    print("="*60)
    print(classification_report(y_test, y_pred,
                               target_names=['Disengaged', 'Partially Engaged', 'Engaged', 'Highly Engaged']))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
               xticklabels=['Disengaged', 'Partially', 'Engaged', 'Highly'],
               yticklabels=['Disengaged', 'Partially', 'Engaged', 'Highly'])
    plt.title(f'Confusion Matrix - {model_data["model_type"]}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    output_path = Path(__file__).parent / 'confusion_matrix.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Confusion matrix saved to: {output_path}")
    
    # Feature importance (if available)
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': model_data['feature_names'],
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n" + "="*60)
        print("Top 10 Most Important Features:")
        print("="*60)
        print(feature_importance.head(10).to_string(index=False))
        
        # Plot
        plt.figure(figsize=(12, 6))
        sns.barplot(data=feature_importance.head(10), x='importance', y='feature')
        plt.title(f'Feature Importance - {model_data["model_type"]}')
        plt.xlabel('Importance')
        plt.tight_layout()
        
        output_path = Path(__file__).parent / 'feature_importance.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Feature importance plot saved to: {output_path}")

def main():
    """Main evaluation pipeline."""
    print("🔍 Loading model for evaluation...")
    
    # Load model
    model_data = load_model()
    print(f"   Model type: {model_data['model_type']}")
    print(f"   Validation accuracy: {model_data['val_accuracy']:.4f}")
    
    # Load test data
    print("\n📊 Loading test data...")
    from generate_training_data import generate_dataset
    df = pd.read_csv(Path(__file__).parent / 'training_data.csv')
    
    X = df.drop('engagement_level', axis=1)
    y = df['engagement_level']
    
    # Map labels
    label_map = {1: 3, 2: 2, 3: 1, 4: 0}
    y = y.map(label_map)
    
    # Split (use same seed as training)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Evaluate
    evaluate_model(model_data, X_test, y_test)
    
    print("\n🎉 Evaluation complete!")

if __name__ == "__main__":
    main()
