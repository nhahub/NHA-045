"""
generate_training_data.py - Synthetic Engagement Data Generator
=================================================================

Generates realistic synthetic training data for engagement classification.

Features (19 total):
- Pitch statistics (mean, std, min, max, p25, p50, p75)
- Yaw statistics (mean, std, min, max, p25, p50, p75)
- EAR statistics (mean, std, min, max, p25, p50, p75)
- Blink count, blink rate
- Face ratio, pitch stability, yaw stability

Labels:
- 1: Highly Engaged
- 2: Engaged
- 3: Partially Engaged
- 4: Disengaged
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Engagement patterns (mean, std for each feature)
ENGAGEMENT_PATTERNS = {
    1: {  # Highly Engaged
        'pitch_mean': (0, 5),      # Looking straight
        'yaw_mean': (0, 5),        # Looking straight
        'ear_mean': (0.25, 0.03),  # Normal eye opening
        'blink_rate': (0.25, 0.1), # Normal blink rate
        'face_ratio': (0.95, 0.05), # Almost always visible
        'stability': (0.9, 0.05)    # Very stable
    },
    2: {  # Engaged
        'pitch_mean': (0, 8),
        'yaw_mean': (0, 8),
        'ear_mean': (0.24, 0.04),
        'blink_rate': (0.3, 0.12),
        'face_ratio': (0.85, 0.1),
        'stability': (0.75, 0.1)
    },
    3: {  # Partially Engaged
        'pitch_mean': (0, 15),     # More head movement
        'yaw_mean': (0, 15),
        'ear_mean': (0.22, 0.05),
        'blink_rate': (0.4, 0.15), # Higher blink rate
        'face_ratio': (0.7, 0.15),
        'stability': (0.6, 0.15)
    },
    4: {  # Disengaged
        'pitch_mean': (5, 20),     # Looking away
        'yaw_mean': (10, 20),
        'ear_mean': (0.20, 0.06),  # Drowsy or stressed
        'blink_rate': (0.6, 0.2),  # Very high or very low
        'face_ratio': (0.5, 0.2),  # Often not visible
        'stability': (0.4, 0.2)    # Very unstable
    }
}

def generate_samples(engagement_level, n_samples):
    """Generate samples for a specific engagement level."""
    pattern = ENGAGEMENT_PATTERNS[engagement_level]
    
    samples = []
    for _ in range(n_samples):
        # Gaze angles (pitch/yaw)
        pitch_mean = np.random.normal(*pattern['pitch_mean'])
        yaw_mean = np.random.normal(*pattern['yaw_mean'])
        
        # Add variability (std, min, max, percentiles)
        pitch_std = abs(np.random.normal(3, 1.5))
        yaw_std = abs(np.random.normal(3, 1.5))
        
        pitch_min = pitch_mean - np.random.uniform(5, 15)
        pitch_max = pitch_mean + np.random.uniform(5, 15)
        yaw_min = yaw_mean - np.random.uniform(5, 15)
        yaw_max = yaw_mean + np.random.uniform(5, 15)
        
        # EAR (Eye Aspect Ratio)
        ear_mean = np.random.normal(*pattern['ear_mean'])
        ear_std = abs(np.random.normal(0.02, 0.01))
        ear_min = max(0.1, ear_mean - np.random.uniform(0.02, 0.05))
        ear_max = min(0.35, ear_mean + np.random.uniform(0.02, 0.05))
        
        # Blink metrics
        blink_count = int(abs(np.random.normal(20, 10)))
        blink_rate = abs(np.random.normal(*pattern['blink_rate']))
        
        # Face presence and stability
        face_ratio = np.clip(np.random.normal(*pattern['face_ratio']), 0, 1)
        stability = np.clip(np.random.normal(*pattern['stability']), 0, 1)
        
        sample = {
            'pitch_mean': pitch_mean,
            'pitch_std': pitch_std,
            'pitch_min': pitch_min,
            'pitch_max': pitch_max,
            'pitch_p25': pitch_mean - pitch_std * 0.67,
            'pitch_p50': pitch_mean,
            'pitch_p75': pitch_mean + pitch_std * 0.67,
            
            'yaw_mean': yaw_mean,
            'yaw_std': yaw_std,
            'yaw_min': yaw_min,
            'yaw_max': yaw_max,
            'yaw_p25': yaw_mean - yaw_std * 0.67,
            'yaw_p50': yaw_mean,
            'yaw_p75': yaw_mean + yaw_std * 0.67,
            
            'ear_mean': ear_mean,
            'ear_std': ear_std,
            'ear_min': ear_min,
            'ear_max': ear_max,
            'ear_p25': ear_mean - ear_std * 0.67,
            'ear_p50': ear_mean,
            'ear_p75': ear_mean + ear_std * 0.67,
            
            'blink_count': blink_count,
            'blink_rate': blink_rate,
            'face_ratio': face_ratio,
            'pitch_stab': stability,
            'yaw_stab': stability,
            
            'engagement_level': engagement_level
        }
        samples.append(sample)
    
    return samples

def generate_dataset(n_samples_per_class=1000, output_path='training_data.csv'):
    """Generate complete training dataset."""
    print(f"Generating {n_samples_per_class} samples per class...")
    
    all_samples = []
    for level in [1, 2, 3, 4]:
        print(f"  - Generating engagement level {level}...")
        samples = generate_samples(level, n_samples_per_class)
        all_samples.extend(samples)
    
    df = pd.DataFrame(all_samples)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    output_file = Path(__file__).parent / output_path
    df.to_csv(output_file, index=False)
    print(f"\n✅ Dataset saved to: {output_file}")
    print(f"   Total samples: {len(df)}")
    print(f"   Class distribution:\n{df['engagement_level'].value_counts().sort_index()}")
    
    return df

if __name__ == "__main__":
    df = generate_dataset(n_samples_per_class=1000)
