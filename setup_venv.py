"""
Automated virtual environment setup for Timetable Generator
Run once: python setup_venv.py
"""
import subprocess
import sys
import os
from pathlib import Path

def create_venv():
    venv_path = Path("venv")
    
    print("🔧 Setting up virtual environment...")
    print("=" * 60)
    
    # Check if venv already exists
    if venv_path.exists():
        print("⚠️  Virtual environment already exists!")
        response = input("Delete and recreate? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled.")
            return False
        
        # Delete existing venv
        import shutil
        print("🗑️  Deleting old virtual environment...")
        shutil.rmtree(venv_path)
    
    # Create new virtual environment
    print("📦 Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # Determine activation command based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        activate_cmd = "venv\\Scripts\\activate"
    else:
        pip_path = venv_path / "bin" / "pip"
        activate_cmd = "source venv/bin/activate"
    
    # Install dependencies
    print("\n📥 Installing dependencies...")
    subprocess.check_call([
        str(pip_path), "install", "-r", "requirements.txt"
    ])
    
    print("\n" + "=" * 60)
    print("✅ Virtual environment setup complete!")
    print("\n📋 Next steps:")
    print(f"   1. Activate venv:  {activate_cmd}")
    print("   2. cd project")
    print("   3. python main.py --configure")
    print("   4. python main.py")
    print("\n💡 To deactivate later: deactivate")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        create_venv()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)