#!/usr/bin/env python3
import os
from PIL import Image
import sys

def optimize_image(input_path, max_width=400, max_height=400, quality=85):
    """Optimize an image for web use"""
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return False
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_path)
        
        with Image.open(input_path) as img:
            print(f"📁 Processing: {input_path}")
            print(f"   Original: {img.size[0]}x{img.size[1]} ({original_size:,} bytes)")
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resize if needed
            if img.size[0] > max_width or img.size[1] > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Create optimized filename
            name, ext = os.path.splitext(input_path)
            optimized_path = f"{name}_optimized.jpg"
            
            # Save as JPEG with optimization
            img.save(optimized_path, 'JPEG', optimize=True, quality=quality)
            
            # Get new file size
            new_size = os.path.getsize(optimized_path)
            reduction = ((original_size - new_size) / original_size * 100)
            
            print(f"   Optimized: {img.size[0]}x{img.size[1]} ({new_size:,} bytes)")
            print(f"   ✅ Saved {reduction:.1f}% ({original_size - new_size:,} bytes)")
            print(f"   📂 Output: {optimized_path}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error processing {input_path}: {e}")
        return False

def main():
    print("🚀 Starting image optimization...")
    
    # List of images to optimize
    images_to_optimize = [
        ("static/apple-touch-icon.png", 180, 180),  # Apple touch icon standard size
        ("static/slide_analyzer/images/lamla_logo.png", 200, 200),  # Logo
        ("static/slide_analyzer/images/student.jpeg", 300, 300),  # Student image
        ("static/slide_analyzer/images/incognito.png", 100, 100),  # Incognito
        ("static/slide_analyzer/images/profile_default.png", 150, 150),  # Profile default
    ]
    
    optimized_count = 0
    total_saved = 0
    
    for img_path, max_w, max_h in images_to_optimize:
        if os.path.exists(img_path):
            original_size = os.path.getsize(img_path)
            if optimize_image(img_path, max_w, max_h):
                optimized_count += 1
                # Calculate savings
                name, ext = os.path.splitext(img_path)
                optimized_path = f"{name}_optimized.jpg"
                if os.path.exists(optimized_path):
                    new_size = os.path.getsize(optimized_path)
                    total_saved += (original_size - new_size)
            print()  # Empty line for readability
        else:
            print(f"⚠️  File not found: {img_path}")
    
    print(f"🎉 Optimization complete!")
    print(f"   Optimized {optimized_count} images")
    print(f"   Total space saved: {total_saved:,} bytes ({total_saved/1024/1024:.1f} MB)")
    print()
    print("📝 Next steps:")
    print("   1. Review optimized images")
    print("   2. Replace original files if satisfied with quality")
    print("   3. Update template references if needed")

if __name__ == "__main__":
    main()
