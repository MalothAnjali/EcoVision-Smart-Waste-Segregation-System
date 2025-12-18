"""
Prepare and analyze the dataset for training
"""
import os
from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = BASE_DIR / "DataSet"
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"

def analyze_dataset():
    """Analyze dataset structure and images"""
    
    print("=" * 80)
    print("📊 Dataset Analysis")
    print("=" * 80)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    # Collect statistics
    stats = defaultdict(lambda: {
        'count': 0,
        'sizes': [],
        'formats': [],
        'corrupted': []
    })
    
    total_images = 0
    
    # Scan dataset
    print(f"\n📁 Scanning dataset at: {DATASET_DIR}")
    
    for category_dir in DATASET_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        print(f"\n   Analyzing category: {category_name}")
        
        # Recursively find all images
        for img_path in category_dir.rglob('*'):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
                try:
                    # Open image to verify it's valid
                    with Image.open(img_path) as img:
                        stats[category_name]['count'] += 1
                        stats[category_name]['sizes'].append(img.size)
                        stats[category_name]['formats'].append(img.format)
                        total_images += 1
                        
                except Exception as e:
                    stats[category_name]['corrupted'].append(str(img_path))
                    print(f"      ⚠️  Corrupted image: {img_path.name} - {e}")
        
        print(f"      ✓ Found {stats[category_name]['count']} valid images")
        if stats[category_name]['corrupted']:
            print(f"      ⚠️  Found {len(stats[category_name]['corrupted'])} corrupted images")
    
    # Display statistics
    print("\n" + "=" * 80)
    print("📈 Dataset Statistics")
    print("=" * 80)
    
    print(f"\nTotal Images: {total_images}")
    print(f"Total Categories: {len(stats)}")
    print("\nPer-Category Breakdown:")
    
    for category, data in sorted(stats.items()):
        print(f"\n  {category}:")
        print(f"    Images: {data['count']}")
        print(f"    Percentage: {data['count']/total_images*100:.1f}%")
        
        if data['sizes']:
            widths = [s[0] for s in data['sizes']]
            heights = [s[1] for s in data['sizes']]
            print(f"    Size range: {min(widths)}x{min(heights)} to {max(widths)}x{max(heights)}")
            print(f"    Average size: {int(np.mean(widths))}x{int(np.mean(heights))}")
        
        if data['formats']:
            formats = set(data['formats'])
            print(f"    Formats: {', '.join(formats)}")
        
        if data['corrupted']:
            print(f"    ⚠️  Corrupted: {len(data['corrupted'])}")
    
    # Check for class imbalance
    print("\n" + "=" * 80)
    print("⚖️  Class Balance Analysis")
    print("=" * 80)
    
    counts = [data['count'] for data in stats.values()]
    max_count = max(counts)
    min_count = min(counts)
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    
    print(f"\nImbalance Ratio: {imbalance_ratio:.2f}:1")
    
    if imbalance_ratio > 3:
        print("⚠️  WARNING: Significant class imbalance detected!")
        print("   Consider using class weights or data augmentation for minority classes.")
    else:
        print("✓ Dataset is reasonably balanced.")
    
    # Visualization
    print("\n📊 Generating visualizations...")
    visualize_dataset(stats, total_images)
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 Recommendations")
    print("=" * 80)
    
    if total_images < 100:
        print("\n⚠️  Dataset is quite small (<100 images)")
        print("   Recommendations:")
        print("   - Use aggressive data augmentation")
        print("   - Consider collecting more images")
        print("   - Use transfer learning (already implemented)")
    elif total_images < 500:
        print("\n✓ Dataset size is acceptable")
        print("   - Data augmentation will help improve generalization")
        print("   - Transfer learning is recommended")
    else:
        print("\n✓ Dataset size is good for training")
    
    # Remove corrupted images
    total_corrupted = sum(len(data['corrupted']) for data in stats.values())
    if total_corrupted > 0:
        print(f"\n⚠️  Found {total_corrupted} corrupted images")
        response = input("   Do you want to remove them? (y/n): ")
        if response.lower() == 'y':
            remove_corrupted_images(stats)
    
    print("\n" + "=" * 80)
    print("✅ Dataset analysis complete!")
    print("=" * 80)

def visualize_dataset(stats, total_images):
    """Create visualizations of dataset statistics"""
    
    categories = list(stats.keys())
    counts = [stats[cat]['count'] for cat in categories]
    
    # Color scheme matching class colors
    colors = ['#22c55e', '#ef4444', '#eab308', '#3b82f6']
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Bar chart
    axes[0].bar(categories, counts, color=colors[:len(categories)])
    axes[0].set_xlabel('Category')
    axes[0].set_ylabel('Number of Images')
    axes[0].set_title('Images per Category')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Add count labels on bars
    for i, (cat, count) in enumerate(zip(categories, counts)):
        axes[0].text(i, count + max(counts)*0.02, str(count), 
                    ha='center', va='bottom', fontweight='bold')
    
    # Pie chart
    axes[1].pie(counts, labels=categories, autopct='%1.1f%%', 
                colors=colors[:len(categories)], startangle=90)
    axes[1].set_title('Dataset Distribution')
    
    plt.tight_layout()
    plot_path = OUTPUT_DIR / 'dataset_analysis.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"   Saved plot: {plot_path}")
    plt.close()

def remove_corrupted_images(stats):
    """Remove corrupted images from dataset"""
    removed_count = 0
    
    for category, data in stats.items():
        for img_path in data['corrupted']:
            try:
                Path(img_path).unlink()
                removed_count += 1
                print(f"   Removed: {img_path}")
            except Exception as e:
                print(f"   Error removing {img_path}: {e}")
    
    print(f"\n✓ Removed {removed_count} corrupted images")

if __name__ == "__main__":
    if not DATASET_DIR.exists():
        print(f"❌ Error: Dataset directory not found at {DATASET_DIR}")
        exit(1)
    
    analyze_dataset()