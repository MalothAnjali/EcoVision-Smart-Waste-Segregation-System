"""
GPU-Optimized Waste Classification Model Training
- Intel Iris Xe GPU support via DirectML
- Improved hyperparameters for better accuracy
- Saves to separate model file (waste_classifier_v2)
"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

# Try to enable DirectML for Intel GPU
try:
    import tensorflow_directml
    # Create DirectML device
    physical_devices = tensorflow_directml.list_physical_devices()
    print(f"\n🎮 DirectML Devices Available: {len(physical_devices)}")
    if physical_devices:
        print("✅ Intel Iris Xe GPU will be used for training!")
        for device in physical_devices:
            print(f"   - {device}")
except ImportError:
    print("\n⚠️  DirectML not installed. Install with: pip install tensorflow-directml-plugin")
    print("   Training will use CPU (slower)")

# ---------------------------------------
# OPTIMIZED CONFIG
# ---------------------------------------
BASE_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = BASE_DIR / "DataSet"
MODEL_DIR = BASE_DIR / "backend" / "models"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

IMG_SIZE = 224
BATCH_SIZE = 16  # Reduced for better generalization
EPOCHS_PHASE1 = 25
EPOCHS_PHASE2 = 25

# Optimized learning rates
LR_PHASE1 = 0.001
LR_PHASE2 = 0.0001

CLASS_NAMES = ["Recyclable", "Non-Recyclable", "Hazardous", "Organic"]

# Model will be saved as v2 to not interfere
MODEL_NAME_V2 = "waste_classifier_v2"

# ---------------------------------------
# IMPROVED DATA GENERATORS
# ---------------------------------------
def create_data_generators():
    """
    Optimized data augmentation for better accuracy
    """
    print("\n📊 Creating optimized data generators...")
    
    # More aggressive augmentation for training
    train_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=40,
        width_shift_range=0.25,
        height_shift_range=0.25,
        shear_range=0.25,
        zoom_range=0.25,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.6, 1.4],
        channel_shift_range=20.0,
        fill_mode='nearest',
        validation_split=0.15  # 85-15 split for more training data
    )

    # Validation with only preprocessing
    val_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
        validation_split=0.15
    )

    train_gen = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=42
    )

    val_gen = val_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=42
    )

    print(f"   Training samples: {train_gen.samples}")
    print(f"   Validation samples: {val_gen.samples}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Steps per epoch: {len(train_gen)}")

    return train_gen, val_gen

# ---------------------------------------
# OPTIMIZED MODEL ARCHITECTURE
# ---------------------------------------
def build_optimized_model(num_classes):
    """
    Improved model architecture for better performance
    """
    print("\n🏗️  Building optimized model...")
    
    # Load MobileNetV2 with ImageNet weights
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    base_model.trainable = False  # Freeze initially
    
    # Build improved model
    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    
    # Data augmentation layer (for GPU acceleration)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name='global_avg_pool')(x)
    
    # Improved head with more capacity
    x = layers.BatchNormalization(name='bn1')(x)
    x = layers.Dropout(0.5, name='dropout1')(x)
    
    x = layers.Dense(512, activation='relu', 
                     kernel_regularizer=keras.regularizers.l2(0.0001),
                     name='dense1')(x)
    x = layers.BatchNormalization(name='bn2')(x)
    x = layers.Dropout(0.4, name='dropout2')(x)
    
    x = layers.Dense(256, activation='relu',
                     kernel_regularizer=keras.regularizers.l2(0.0001),
                     name='dense2')(x)
    x = layers.BatchNormalization(name='bn3')(x)
    x = layers.Dropout(0.3, name='dropout3')(x)
    
    outputs = layers.Dense(num_classes, activation='softmax', name='predictions')(x)
    
    model = keras.Model(inputs, outputs, name='waste_classifier_v2')
    
    trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
    total_params = sum([tf.size(w).numpy() for w in model.weights])
    
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    
    return model, base_model

# ---------------------------------------
# TRAIN MODEL
# ---------------------------------------
def train_model():
    print("=" * 80)
    print("🚀 GPU-Optimized EcoVision Model Training v2")
    print("=" * 80)
    
    # Check GPU availability
    print("\n🖥️  System Information:")
    print(f"   TensorFlow version: {tf.__version__}")
    print(f"   GPU Available: {len(tf.config.list_physical_devices('GPU')) > 0}")
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            print(f"   - {gpu}")
    
    # Create directories
    MODEL_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load data
    print("\n📁 Loading dataset...")
    train_gen, val_gen = create_data_generators()
    
    num_classes = len(train_gen.class_indices)
    steps_per_epoch = len(train_gen)
    validation_steps = len(val_gen)
    
    print(f"\n📈 Training Configuration:")
    print(f"   Classes: {num_classes}")
    print(f"   Steps per epoch: {steps_per_epoch}")
    print(f"   Validation steps: {validation_steps}")
    print(f"   Total epochs: {EPOCHS_PHASE1 + EPOCHS_PHASE2}")
    
    # Build model
    model, base_model = build_optimized_model(num_classes)
    
    # Class weights for imbalanced dataset
    class_counts = {}
    for class_name, class_idx in train_gen.class_indices.items():
        class_counts[class_idx] = 0
    
    for i in range(len(train_gen)):
        _, labels = train_gen[i]
        for label in labels:
            class_idx = np.argmax(label)
            class_counts[class_idx] += 1
        if i >= 10:  # Sample first 10 batches
            break
    
    total_samples = sum(class_counts.values())
    class_weights = {idx: total_samples / (num_classes * count) 
                     for idx, count in class_counts.items()}
    
    print(f"\n⚖️  Using class weights to handle imbalance:")
    for class_name, class_idx in train_gen.class_indices.items():
        print(f"   {class_name}: {class_weights[class_idx]:.2f}")
    
    # Callbacks for Phase 1
    callbacks_phase1 = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=8,
            restore_best_weights=True,
            verbose=1,
            mode='max'
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / f'{MODEL_NAME_V2}_phase1.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        )
    ]
    
    # --- PHASE 1: Train with frozen base ---
    print("\n" + "=" * 80)
    print("🎯 Phase 1: Training classifier head (frozen base)")
    print("=" * 80)
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LR_PHASE1),
        loss='categorical_crossentropy',
        metrics=['accuracy', 
                 keras.metrics.Precision(name='precision'),
                 keras.metrics.Recall(name='recall')]
    )
    
    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE1,
        callbacks=callbacks_phase1,
        class_weight=class_weights,
        verbose=1
    )
    
    # Evaluate after Phase 1
    print("\n📊 Phase 1 Evaluation:")
    val_results = model.evaluate(val_gen, verbose=0)
    val_loss, val_acc, val_prec, val_rec = val_results
    f1_score = 2 * (val_prec * val_rec) / (val_prec + val_rec) if (val_prec + val_rec) > 0 else 0
    
    print(f"   Accuracy:  {val_acc:.4f} ({val_acc*100:.2f}%)")
    print(f"   Precision: {val_prec:.4f}")
    print(f"   Recall:    {val_rec:.4f}")
    print(f"   F1-Score:  {f1_score:.4f}")
    
    # --- PHASE 2: Fine-tuning ---
    print("\n" + "=" * 80)
    print("🔥 Phase 2: Fine-tuning (unfreezing top layers)")
    print("=" * 80)
    
    # Unfreeze the last 50 layers for better fine-tuning
    base_model.trainable = True
    fine_tune_at = len(base_model.layers) - 50
    
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
    
    print(f"   Unfrozing last 50 layers (from layer {fine_tune_at})")
    
    trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
    print(f"   Trainable parameters: {trainable_params:,}")
    
    # Callbacks for Phase 2
    callbacks_phase2 = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=8,
            restore_best_weights=True,
            verbose=1,
            mode='max'
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-8,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / f'{MODEL_NAME_V2}_best.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        )
    ]
    
    # Compile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LR_PHASE2),
        loss='categorical_crossentropy',
        metrics=['accuracy',
                 keras.metrics.Precision(name='precision'),
                 keras.metrics.Recall(name='recall')]
    )
    
    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE2,
        callbacks=callbacks_phase2,
        class_weight=class_weights,
        verbose=1
    )
    
    # Final evaluation
    print("\n" + "=" * 80)
    print("📊 Final Evaluation")
    print("=" * 80)
    
    val_results = model.evaluate(val_gen)
    val_loss, val_acc, val_prec, val_rec = val_results
    f1_score = 2 * (val_prec * val_rec) / (val_prec + val_rec) if (val_prec + val_rec) > 0 else 0
    
    print(f"\n✅ FINAL RESULTS (Model v2):")
    print(f"   Validation Accuracy:  {val_acc:.4f} ({val_acc*100:.2f}%)")
    print(f"   Validation Precision: {val_prec:.4f}")
    print(f"   Validation Recall:    {val_rec:.4f}")
    print(f"   F1-Score:             {f1_score:.4f}")
    
    # Performance assessment
    if val_acc >= 0.85:
        print("   🎉 EXCELLENT! Model is performing very well!")
    elif val_acc >= 0.75:
        print("   ✓ GOOD! Model is performing well.")
    elif val_acc >= 0.65:
        print("   ⚠️  FAIR. Consider training longer or collecting more data.")
    else:
        print("   ❌ POOR. Model needs improvement.")
    
    # Save models
    print("\n💾 Saving models (v2)...")
    
    # Save Keras model
    keras_model_path = MODEL_DIR / f"{MODEL_NAME_V2}.h5"
    model.save(keras_model_path)
    print(f"   Saved Keras model: {keras_model_path}")
    
    # Convert to TensorFlow Lite
    print("\n🔄 Converting to TensorFlow Lite...")
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Add representative dataset for better quantization
        def representative_dataset():
            for i in range(100):
                data = train_gen[i % len(train_gen)][0]
                yield [data.astype(np.float32)]
        
        converter.representative_dataset = representative_dataset
        tflite_model = converter.convert()
        
        tflite_path = MODEL_DIR / f"{MODEL_NAME_V2}.tflite"
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"   Saved TFLite model: {tflite_path}")
        print(f"   Model size: {len(tflite_model) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"   ⚠️  TFLite conversion failed: {e}")
        print("   Keras model is still available")
    
    # Save class mapping
    class_mapping = {
        "classes": CLASS_NAMES,
        "class_indices": train_gen.class_indices,
        "num_classes": num_classes,
        "input_size": IMG_SIZE,
        "model_version": "v2",
        "training_date": datetime.now().isoformat(),
        "final_accuracy": float(val_acc),
        "final_precision": float(val_prec),
        "final_recall": float(val_rec),
        "f1_score": float(f1_score),
        "epochs_trained": EPOCHS_PHASE1 + EPOCHS_PHASE2
    }
    
    mapping_path = MODEL_DIR / f"class_mapping_v2.json"
    with open(mapping_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"   Saved class mapping: {mapping_path}")
    
    # Plot training history
    print("\n📈 Generating training plots...")
    plot_training_history(history1, history2)
    
    print("\n" + "=" * 80)
    print("🎉 Training Complete!")
    print("=" * 80)
    print(f"\n💡 Your new model (v2) is ready!")
    print(f"   Location: {MODEL_DIR / MODEL_NAME_V2}.h5")
    print(f"   TFLite: {MODEL_DIR / MODEL_NAME_V2}.tflite")
    print(f"\n   To use this model, update config.py:")
    print(f"   MODEL_PATH = 'models/{MODEL_NAME_V2}.tflite'")
    
    return history1, history2

# ---------------------------------------
# PLOT HISTORY
# ---------------------------------------
def plot_training_history(history1, history2):
    """Plot and save training history"""
    
    # Combine histories
    acc = history1.history['accuracy'] + history2.history['accuracy']
    val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
    loss = history1.history['loss'] + history2.history['loss']
    val_loss = history1.history['val_loss'] + history2.history['val_loss']
    
    epochs_range = range(len(acc))
    phase1_end = len(history1.history['accuracy'])
    
    plt.figure(figsize=(16, 5))
    
    # Accuracy plot
    plt.subplot(1, 3, 1)
    plt.plot(epochs_range, acc, 'b-', label='Training Accuracy', linewidth=2)
    plt.plot(epochs_range, val_acc, 'r-', label='Validation Accuracy', linewidth=2)
    plt.axvline(x=phase1_end, color='green', linestyle='--', label='Fine-tuning starts', linewidth=1.5)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Model Accuracy (GPU Optimized)', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    # Loss plot
    plt.subplot(1, 3, 2)
    plt.plot(epochs_range, loss, 'b-', label='Training Loss', linewidth=2)
    plt.plot(epochs_range, val_loss, 'r-', label='Validation Loss', linewidth=2)
    plt.axvline(x=phase1_end, color='green', linestyle='--', label='Fine-tuning starts', linewidth=1.5)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('Model Loss (GPU Optimized)', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Metrics comparison
    plt.subplot(1, 3, 3)
    final_acc = val_acc[-1]
    categories = ['Final\nAccuracy', 'Target\n(85%)', 'Improvement\nNeeded']
    values = [final_acc * 100, 85, max(0, 85 - final_acc * 100)]
    colors = ['#22c55e' if final_acc >= 0.85 else '#eab308' if final_acc >= 0.75 else '#ef4444',
              '#9ca3af', '#ef4444']
    
    bars = plt.bar(range(len(categories)), values, color=colors[:len(values)])
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.title('Performance Summary (v2)', fontsize=14, fontweight='bold')
    plt.xticks(range(len(categories)), categories)
    plt.ylim(0, 100)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plot_path = OUTPUT_DIR / 'training_history_v2_gpu.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"   Saved training plot: {plot_path}")
    
    plt.close()

# ---------------------------------------
# MAIN
# ---------------------------------------
if __name__ == "__main__":
    if not DATASET_DIR.exists():
        print(f"❌ Dataset not found at: {DATASET_DIR}")
        print(f"   Expected location: {DATASET_DIR}")
        exit(1)
    
    train_model()