#!/usr/bin/env python3
"""
Simple dependency installer for Timetable Generator
Run this before first use: python install_dependencies.py
"""
import subprocess
import sys

def install():
    print("🔧 Installing dependencies...")
    print("=" * 60)
    
    try:
        # Install from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("\n" + "=" * 60)
        print("✅ All dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("   1. cd project")
        print("   2. python main.py --configure")
        print("   3. python main.py")
        print("=" * 60)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("\nTry manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    install()