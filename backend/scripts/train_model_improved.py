"""
Improved Waste Classification Model Training
- Correct MobileNetV2 preprocessing
- Better callbacks and monitoring
- Converts to TFLite
"""
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

# ---------------------------------------
# CONFIG
# ---------------------------------------
BASE_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = BASE_DIR / "DataSet"
MODEL_DIR = BASE_DIR / "backend" / "models"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_FROZEN = 30  # Increased
EPOCHS_FINE = 20    # Increased

LR_FROZEN = 1e-3
LR_FINE = 1e-5

CLASS_NAMES = ["Recyclable", "Non-Recyclable", "Hazardous", "Organic"]

# ---------------------------------------
# DATA GENERATORS (CORRECT PREPROCESSING)
# ---------------------------------------
def create_data_generators():
    """
    Correct preprocessing using MobileNetV2 preprocessing
    """
    print("\n📊 Creating data generators...")
    
    # Training augmentation
    train_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest',
        validation_split=0.2
    )

    # Validation generator (NO augmentation)
    val_datagen = ImageDataGenerator(
        preprocessing_function=keras.applications.mobilenet_v2.preprocess_input,
        validation_split=0.2
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
    print(f"   Classes found: {train_gen.class_indices}")

    return train_gen, val_gen

# ---------------------------------------
# BUILD MODEL (IMPROVED ARCHITECTURE)
# ---------------------------------------
def build_model(num_classes):
    """Build improved MobileNetV2-based model"""
    print("\n🏗️  Building model...")
    
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )

    base_model.trainable = False  # Freeze initially

    # Build model
    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = keras.Model(inputs, outputs)
    
    print(f"   Total parameters: {model.count_params():,}")
    
    return model, base_model

# ---------------------------------------
# TRAIN MODEL
# ---------------------------------------
def train_model():
    print("=" * 80)
    print("🚀 Starting EcoVision Model Training (IMPROVED)")
    print("=" * 80)

    # Create directories
    MODEL_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load data
    print("\n📁 Loading dataset...")
    train_gen, val_gen = create_data_generators()
    
    # Check if dataset is too small
    if train_gen.samples < 100:
        print("\n⚠️  WARNING: Dataset is very small!")
        print("   Recommendation: Collect more images or expect lower accuracy")
    
    num_classes = len(train_gen.class_indices)

    # Build model
    model, base_model = build_model(num_classes)

    # Callbacks for Phase 1
    callbacks_phase1 = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / 'best_model_phase1.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # --- PHASE 1: Train with frozen base ---
    print("\n" + "=" * 80)
    print("🎯 Phase 1: Training with frozen base...")
    print("=" * 80)

    model.compile(
        optimizer=keras.optimizers.Adam(LR_FROZEN),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )

    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_FROZEN,
        callbacks=callbacks_phase1,
        verbose=1
    )

    # Evaluate after Phase 1
    val_loss, val_acc, val_prec, val_rec = model.evaluate(val_gen, verbose=0)
    print(f"\n📊 Phase 1 Results:")
    print(f"   Accuracy:  {val_acc:.4f} ({val_acc*100:.2f}%)")
    print(f"   Precision: {val_prec:.4f}")
    print(f"   Recall:    {val_rec:.4f}")

    # --- PHASE 2: Fine-tuning ---
    print("\n" + "=" * 80)
    print("🔥 Phase 2: Fine-tuning...")
    print("=" * 80)

    # Unfreeze top layers
    base_model.trainable = True
    fine_tune_at = len(base_model.layers) - 30  # Last 30 layers
    
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    print(f"   Unfrozing last 30 layers (from layer {fine_tune_at})")

    # Callbacks for Phase 2
    callbacks_phase2 = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=6,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-8,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / 'best_model_final.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    model.compile(
        optimizer=keras.optimizers.Adam(LR_FINE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )

    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_FINE,
        callbacks=callbacks_phase2,
        verbose=1
    )

    # Final evaluation
    print("\n" + "=" * 80)
    print("📊 Final Evaluation")
    print("=" * 80)
    
    val_loss, val_acc, val_prec, val_rec = model.evaluate(val_gen)
    
    print(f"\n✅ FINAL RESULTS:")
    print(f"   Validation Accuracy:  {val_acc:.4f} ({val_acc*100:.2f}%)")
    print(f"   Validation Precision: {val_prec:.4f}")
    print(f"   Validation Recall:    {val_rec:.4f}")
    print(f"   F1-Score:             {2 * (val_prec * val_rec) / (val_prec + val_rec):.4f}")

    # Accuracy assessment
    if val_acc >= 0.85:
        print("   🎉 EXCELLENT! Model is performing very well!")
    elif val_acc >= 0.70:
        print("   ✓ GOOD! Model is performing reasonably well.")
    elif val_acc >= 0.55:
        print("   ⚠️  FAIR. Model needs improvement - consider more data.")
    else:
        print("   ❌ POOR. Model needs significant improvement.")

    # Save models
    print("\n💾 Saving models...")
    
    # Save Keras model
    keras_model_path = MODEL_DIR / "waste_classifier.h5"
    model.save(keras_model_path)
    print(f"   Saved Keras model: {keras_model_path}")

    # Convert to TensorFlow Lite
    print("\n🔄 Converting to TensorFlow Lite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    try:
        tflite_model = converter.convert()
        
        tflite_path = MODEL_DIR / "waste_classifier.tflite"
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"   Saved TFLite model: {tflite_path}")
        print(f"   Model size: {len(tflite_model) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"   ⚠️  TFLite conversion failed: {e}")
        print("   Keras model is still available for use")

    # Save class mapping
    class_mapping = {
        "classes": CLASS_NAMES,
        "class_indices": train_gen.class_indices,
        "num_classes": num_classes,
        "input_size": IMG_SIZE,
        "training_date": datetime.now().isoformat(),
        "final_accuracy": float(val_acc),
        "final_precision": float(val_prec),
        "final_recall": float(val_rec)
    }

    mapping_path = MODEL_DIR / "class_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"   Saved class mapping: {mapping_path}")

    # Plot training history
    print("\n📈 Generating training plots...")
    plot_training_history(history1, history2)

    print("\n" + "=" * 80)
    print("🎉 Training Complete!")
    print("=" * 80)
    print(f"\n💡 Next steps:")
    print(f"   1. Check training plots in: {OUTPUT_DIR}")
    print(f"   2. Start backend: cd backend && python app/main.py")
    print(f"   3. Start frontend: cd frontend && npm run dev")

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
    plt.title('Model Accuracy', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    # Loss plot
    plt.subplot(1, 3, 2)
    plt.plot(epochs_range, loss, 'b-', label='Training Loss', linewidth=2)
    plt.plot(epochs_range, val_loss, 'r-', label='Validation Loss', linewidth=2)
    plt.axvline(x=phase1_end, color='green', linestyle='--', label='Fine-tuning starts', linewidth=1.5)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('Model Loss', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Metrics comparison
    plt.subplot(1, 3, 3)
    final_acc = val_acc[-1]
    categories = ['Accuracy', 'Target\n(85%)', 'Current']
    values = [final_acc * 100, 85, final_acc * 100]
    colors = ['#22c55e' if final_acc >= 0.85 else '#eab308' if final_acc >= 0.70 else '#ef4444']
    
    bars = plt.bar(range(len(categories)), values, color=['#3b82f6', '#9ca3af', colors[0]])
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.title('Performance Summary', fontsize=14, fontweight='bold')
    plt.xticks(range(len(categories)), categories)
    plt.ylim(0, 100)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plot_path = OUTPUT_DIR / 'training_history.png'
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