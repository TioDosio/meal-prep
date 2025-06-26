#!/usr/bin/env python3
"""
Setup script for Nutrition Meal Planner
This script helps users set up the application environment
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_credentials_file():
    """Check if service account credentials file exists"""
    print("\nChecking for Google Sheets credentials...")
    if os.path.exists("service_account_key.json"):
        try:
            with open("service_account_key.json", "r") as f:
                creds = json.load(f)
                if "client_email" in creds:
                    print(f"✅ Credentials file found")
                    print(f"Service account email: {creds['client_email']}")
                    return True
                else:
                    print("❌ Invalid credentials file format")
                    return False
        except json.JSONDecodeError:
            print("❌ Credentials file is not valid JSON")
            return False
    else:
        print("❌ service_account_key.json not found")
        print("\nPlease follow these steps:")
        print("1. Go to Google Cloud Console")
        print("2. Create a service account with Sheets and Drive API access")
        print("3. Download the JSON key file")
        print("4. Rename it to 'service_account_key.json'")
        print("5. Place it in this directory")
        return False

def run_tests():
    """Run application tests"""
    print("\nRunning application tests...")
    try:
        result = subprocess.run([sys.executable, "test_app.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut (Linux/macOS)"""
    if sys.platform.startswith('linux'):
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            shortcut_content = f"""[Desktop Entry]
Name=Nutrition Meal Planner
Comment=Manage recipes, ingredients, and meal planning
Exec={sys.executable} {os.path.abspath('nutrition_meal_planner_final.py')}
Icon=applications-other
Terminal=false
Type=Application
Categories=Office;
"""
            shortcut_path = os.path.join(desktop_path, "NutritionMealPlanner.desktop")
            try:
                with open(shortcut_path, "w") as f:
                    f.write(shortcut_content)
                os.chmod(shortcut_path, 0o755)
                print(f"✅ Desktop shortcut created: {shortcut_path}")
                return True
            except Exception as e:
                print(f"⚠️  Could not create desktop shortcut: {e}")
                return False
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("Nutrition Meal Planner - Setup Script")
    print("=" * 60)
    
    success_count = 0
    total_checks = 4
    
    # Check Python version
    if check_python_version():
        success_count += 1
    
    # Install dependencies
    if install_dependencies():
        success_count += 1
    
    # Check credentials
    if check_credentials_file():
        success_count += 1
    
    # Run tests
    if run_tests():
        success_count += 1
    
    # Create desktop shortcut (optional)
    create_desktop_shortcut()
    
    print("\n" + "=" * 60)
    print(f"Setup completed: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run the application with:")
        print("python3 nutrition_meal_planner_final.py")
    else:
        print("⚠️  Setup completed with some issues.")
        print("Please resolve the issues above before running the application.")
    
    print("\nFor help, see README.md")
    return 0 if success_count == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())

