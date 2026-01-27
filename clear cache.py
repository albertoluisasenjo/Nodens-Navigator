#!/usr/bin/env python3
"""
Clear WebDriver Manager Cache
This script cleans the webdriver-manager cache to force download of latest ChromeDriver
"""

import os
import shutil
from pathlib import Path

def clear_wdm_cache():
    """Clear webdriver-manager cache directory"""
    cache_paths = [
        Path.home() / '.wdm',  # Linux/Mac
        Path.home() / 'AppData' / 'Local' / '.wdm',  # Windows
    ]
    
    cleared = False
    for cache_path in cache_paths:
        if cache_path.exists():
            print(f"🗑️  Found cache at: {cache_path}")
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Cleared cache: {cache_path}")
                cleared = True
            except Exception as e:
                print(f"❌ Error clearing {cache_path}: {e}")
        else:
            print(f"ℹ️  No cache found at: {cache_path}")
    
    return cleared

def clear_selenium_cache():
    """Clear selenium cache directory"""
    selenium_cache = Path.home() / '.cache' / 'selenium'
    
    if selenium_cache.exists():
        print(f"🗑️  Found Selenium cache at: {selenium_cache}")
        try:
            shutil.rmtree(selenium_cache)
            print(f"✅ Cleared Selenium cache")
            return True
        except Exception as e:
            print(f"❌ Error clearing Selenium cache: {e}")
            return False
    else:
        print("ℹ️  No Selenium cache found")
        return False

def main():
    print("="*60)
    print("🧹 WebDriver Manager Cache Cleaner")
    print("="*60)
    print()
    
    wdm_cleared = clear_wdm_cache()
    print()
    selenium_cleared = clear_selenium_cache()
    
    print()
    print("="*60)
    if wdm_cleared or selenium_cleared:
        print("✅ Cache cleared successfully!")
        print()
        print("Next steps:")
        print("1. pip install --upgrade webdriver-manager")
        print("2. streamlit run app.py")
    else:
        print("ℹ️  No cache found to clear")
        print()
        print("This might mean:")
        print("- This is your first run")
        print("- Cache is in a different location")
        print("- You're on a different OS")
    print("="*60)

if __name__ == "__main__":
    main()
