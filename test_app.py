#!/usr/bin/env python3
"""
Test script for the Nutrition Meal Planner application
This script tests the core functionality without requiring a GUI display
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import gspread
        print("[OK] gspread imported successfully")
        
        import qdarkstyle
        print("[OK] qdarkstyle imported successfully")
        
        import matplotlib.pyplot as plt
        print("[OK] matplotlib imported successfully")
        
        import pandas as pd
        print("[OK] pandas imported successfully")
        
        # Test PySide6 imports without creating GUI
        from PySide6.QtCore import Qt, QDate
        print("[OK] PySide6.QtCore imported successfully")
        
        from PySide6.QtWidgets import QApplication
        print("[OK] PySide6.QtWidgets imported successfully")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_google_sheets_manager():
    """Test the GoogleSheetsManager class"""
    print("\nTesting GoogleSheetsManager...")
    try:
        # Import the class from our application
        from nutrition_meal_planner_final import GoogleSheetsManager
        
        # Test initialization (this will try to connect)
        manager = GoogleSheetsManager()
        
        if manager.gc and manager.spreadsheet:
            print("[OK] GoogleSheetsManager connected successfully")
            
            # Test getting worksheet names
            worksheets = [ws.title for ws in manager.spreadsheet.worksheets()]
            print(f"[OK] Found worksheets: {worksheets}")
            
            # Test getting data from a worksheet
            recipes_data = manager.get_all_data("Recipes")
            print(f"[OK] Retrieved {len(recipes_data)} recipes")
            
            ingredients_data = manager.get_all_data("Ingredients")
            print(f"[OK] Retrieved {len(ingredients_data)} ingredients")
            
            return True
        else:
            print("[FAIL] Failed to connect to Google Sheets")
            return False
            
    except Exception as e:
        print(f"[FAIL] GoogleSheetsManager error: {e}")
        return False

def test_application_structure():
    """Test that the application classes can be instantiated"""
    print("\nTesting application structure...")
    try:
        from nutrition_meal_planner_final import (
            RecipeDialog, IngredientDialog, MealPlanDialog,
            RecipeIngredientsDialog, NutritionChart
        )
        print("[OK] All dialog classes imported successfully")
        
        # Test that the main application class can be imported
        from nutrition_meal_planner_final import NutritionMealPlannerApp
        print("[OK] Main application class imported successfully")
        
        return True
    except Exception as e:
        print(f"[FAIL] Application structure error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Nutrition Meal Planner - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_google_sheets_manager():
        tests_passed += 1
    
    if test_application_structure():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("[OK] All tests passed! The application is ready to use.")
        print("\nTo run the application:")
        print("python3 nutrition_meal_planner_final.py")
        return 0
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

