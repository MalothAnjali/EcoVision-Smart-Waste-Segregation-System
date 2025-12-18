"""
Train waste classification model using MobileNetV2
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

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = BASE_DIR / "DataSet"
MODEL_DIR = BASE_DIR / "backend" / "models"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

# Model parameters
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001

# Class names (should match your dataset folders)
CLASS_NAMES = ["Recyclable", "Non-Recyclable", "Hazardous", "Organic"]

def create_data_generators():
    """Create training and validation data generators"""
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        validation_split=0.2  # 80% train, 20% validation
    )
    
    # No augmentation for validation
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )
    
    # Training generator
    train_generator = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=42
    )
    
    # Validation generator
    val_generator = val_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=42
    )
    
    return train_generator, val_generator

def build_model(num_classes):
    """Build MobileNetV2-based transfer learning model"""
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Build model
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model, base_model

def train_model():
    """Main training function"""
    
    print("=" * 80)
    print("🚀 Starting EcoVision Model Training")
    print("=" * 80)
    
    # Create output directory
    MODEL_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create data generators
    print("\n📁 Loading dataset...")
    train_gen, val_gen = create_data_generators()
    
    print(f"   Training samples: {train_gen.samples}")
    print(f"   Validation samples: {val_gen.samples}")
    print(f"   Classes: {train_gen.class_indices}")
    
    # Build model
    print("\n🏗️  Building model...")
    num_classes = len(train_gen.class_indices)
    model, base_model = build_model(num_classes)
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print(f"   Model architecture: MobileNetV2 + Custom Head")
    print(f"   Total parameters: {model.count_params():,}")
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train model (Phase 1: Frozen base)
    print("\n🎯 Phase 1: Training with frozen base model...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # Fine-tuning (Phase 2: Unfreeze some layers)
    print("\n🔥 Phase 2: Fine-tuning model...")
    base_model.trainable = True
    
    # Freeze first 100 layers
    for layer in base_model.layers[:100]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    # Continue training
    history_fine = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=20,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    print("\n📊 Evaluating model...")
    val_loss, val_acc, val_precision, val_recall = model.evaluate(val_gen)
    
    print(f"\n✅ Training Complete!")
    print(f"   Validation Accuracy: {val_acc:.4f}")
    print(f"   Validation Precision: {val_precision:.4f}")
    print(f"   Validation Recall: {val_recall:.4f}")
    
    # Save final model
    print("\n💾 Saving models...")
    
    # Save Keras model
    keras_model_path = MODEL_DIR / "waste_classifier.h5"
    model.save(keras_model_path)
    print(f"   Saved Keras model: {keras_model_path}")
    
    # Convert to TensorFlow Lite
    print("\n🔄 Converting to TensorFlow Lite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Optimization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    # Save TFLite model
    tflite_path = MODEL_DIR / "waste_classifier.tflite"
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"   Saved TFLite model: {tflite_path}")
    print(f"   Model size: {len(tflite_model) / 1024 / 1024:.2f} MB")
    
    # Save class mapping
    class_mapping = {
        "classes": CLASS_NAMES,
        "class_indices": train_gen.class_indices,
        "num_classes": num_classes,
        "input_size": IMG_SIZE,
        "training_date": datetime.now().isoformat()
    }
    
    mapping_path = MODEL_DIR / "class_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"   Saved class mapping: {mapping_path}")
    
    # Plot training history
    print("\n📈 Generating training plots...")
    plot_training_history(history, history_fine)
    
    print("\n" + "=" * 80)
    print("🎉 Training pipeline completed successfully!")
    print("=" * 80)
    print(f"\n💡 Next steps:")
    print(f"   1. Check training plots in: {OUTPUT_DIR}")
    print(f"   2. Start the backend server: cd backend && python app/main.py")
    print(f"   3. Start the frontend: cd frontend && npm run dev")

def plot_training_history(history1, history2):
    """Plot and save training history"""
    
    # Combine histories
    acc = history1.history['accuracy'] + history2.history['accuracy']
    val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
    loss = history1.history['loss'] + history2.history['loss']
    val_loss = history1.history['val_loss'] + history2.history['val_loss']
    
    epochs_range = range(len(acc))
    
    plt.figure(figsize=(15, 5))
    
    # Accuracy plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.axvline(x=len(history1.history['accuracy']), color='r', linestyle='--', label='Fine-tuning starts')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.grid(True)
    
    # Loss plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.axvline(x=len(history1.history['loss']), color='r', linestyle='--', label='Fine-tuning starts')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.grid(True)
    
    plt.tight_layout()
    plot_path = OUTPUT_DIR / 'training_history.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"   Saved training plot: {plot_path}")
    
    plt.close()

if __name__ == "__main__":
    # Check if dataset exists
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found at {DATASET_DIR}")
        print("   Please ensure your DataSet folder is in the correct location.")
        exit(1)
    
    # Start training
    train_model()