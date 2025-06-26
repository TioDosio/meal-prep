import sys
import json
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame, 
                               QTextEdit, QMenuBar, QStatusBar, QGroupBox,
                               QGridLayout, QLineEdit, QComboBox, QSlider,
                               QProgressBar, QCheckBox, QRadioButton, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QSpinBox, QDoubleSpinBox, QDateEdit, QMessageBox,
                               QDialog, QDialogButtonBox, QFormLayout, QScrollArea,
                               QSplitter, QListWidget, QListWidgetItem, QCalendarWidget)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QIcon, QAction
import qdarkstyle
import gspread
from googleapiclient.errors import HttpError
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

class GoogleSheetsManager:
    def __init__(self, service_account_file="service_account_key.json"):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        self.service_account_file = service_account_file
        self.gc = None
        self.spreadsheet = None
        self.connect()

    def connect(self):
        try:
            self.gc = gspread.service_account(filename=self.service_account_file, scopes=self.scopes)
            self.spreadsheet = self.gc.open("Nutrition Meal Planner Database")
            return True
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False

    def get_worksheet(self, sheet_name):
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except Exception as e:
            print(f"Error getting worksheet {sheet_name}: {e}")
            return None

    def get_all_data(self, sheet_name):
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            return worksheet.get_all_records()
        return []

    def add_row(self, sheet_name, data):
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            try:
                worksheet.append_row(data)
                return True
            except Exception as e:
                print(f"Error adding row to {sheet_name}: {e}")
        return False

    def update_row(self, sheet_name, row_index, data):
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            try:
                for col_index, value in enumerate(data, start=1):
                    worksheet.update_cell(row_index, col_index, value)
                return True
            except Exception as e:
                print(f"Error updating row in {sheet_name}: {e}")
        return False

    def delete_row(self, sheet_name, row_index):
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            try:
                worksheet.delete_rows(row_index)
                return True
            except Exception as e:
                print(f"Error deleting row from {sheet_name}: {e}")
        return False

    def clear_recipe_ingredients(self, recipe_name):
        """Clear all ingredients for a specific recipe"""
        worksheet = self.get_worksheet("Recipe_Ingredients")
        if worksheet:
            try:
                all_data = worksheet.get_all_values()
                rows_to_delete = []
                
                for i, row in enumerate(all_data[1:], start=2):  # Skip header row
                    if row and row[0] == recipe_name:  # Recipe Name is in first column
                        rows_to_delete.append(i)
                
                # Delete rows in reverse order to maintain indices
                for row_index in reversed(rows_to_delete):
                    worksheet.delete_rows(row_index)
                
                return True
            except Exception as e:
                print(f"Error clearing recipe ingredients: {e}")
        return False

class MealPlanDialog(QDialog):
    def __init__(self, parent=None, selected_date=None, meal_data=None):
        super().__init__(parent)
        self.selected_date = selected_date or date.today()
        self.meal_data = meal_data
        self.available_recipes = []
        self.init_ui()
        self.load_available_recipes()

    def init_ui(self):
        self.setWindowTitle(f"Plan Meal for {self.selected_date.strftime('%Y-%m-%d')}")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Date display
        date_label = QLabel(f"Date: {self.selected_date.strftime('%A, %B %d, %Y')}")
        date_font = QFont()
        date_font.setBold(True)
        date_label.setFont(date_font)
        layout.addWidget(date_label)

        # Form layout
        form_layout = QFormLayout()

        # Meal type
        self.meal_type_combo = QComboBox()
        self.meal_type_combo.addItems(["Breakfast", "Lunch", "Dinner", "Snack"])
        form_layout.addRow("Meal Type:", self.meal_type_combo)

        # Recipe selection
        self.recipe_combo = QComboBox()
        form_layout.addRow("Recipe:", self.recipe_combo)

        # Portion size
        self.portion_size_spin = QDoubleSpinBox()
        self.portion_size_spin.setMinimum(0.1)
        self.portion_size_spin.setMaximum(10.0)
        self.portion_size_spin.setValue(1.0)
        self.portion_size_spin.setSingleStep(0.1)
        form_layout.addRow("Portion Size:", self.portion_size_spin)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Load data if editing
        if self.meal_data:
            self.load_data()

    def load_available_recipes(self):
        try:
            sheets_manager = self.parent().sheets_manager
            recipes_data = sheets_manager.get_all_data("Recipes")
            self.available_recipes = recipes_data
            
            self.recipe_combo.clear()
            for recipe in recipes_data:
                self.recipe_combo.addItem(recipe.get("Recipe Name", ""))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load recipes: {e}")

    def load_data(self):
        # Set meal type
        meal_type = self.meal_data.get("Meal Type", "Breakfast")
        index = self.meal_type_combo.findText(meal_type)
        if index >= 0:
            self.meal_type_combo.setCurrentIndex(index)

        # Set recipe
        recipe_name = self.meal_data.get("Recipe Name", "")
        index = self.recipe_combo.findText(recipe_name)
        if index >= 0:
            self.recipe_combo.setCurrentIndex(index)

        # Set portion size
        try:
            portion_size = float(self.meal_data.get("Portion Size (for the meal plan, referring to the recipe's portion size)", 1.0))
            self.portion_size_spin.setValue(portion_size)
        except (ValueError, TypeError):
            self.portion_size_spin.setValue(1.0)

    def get_data(self):
        return {
            "Date": self.selected_date.strftime('%Y-%m-%d'),
            "Meal Type": self.meal_type_combo.currentText(),
            "Recipe Name": self.recipe_combo.currentText(),
            "Portion Size (for the meal plan, referring to the recipe's portion size)": self.portion_size_spin.value()
        }

class RecipeIngredientsDialog(QDialog):
    def __init__(self, parent=None, recipe_name="", ingredients_list=None):
        super().__init__(parent)
        self.recipe_name = recipe_name
        self.ingredients_list = ingredients_list or []
        self.available_ingredients = []
        self.recipe_ingredients = []
        self.init_ui()
        self.load_available_ingredients()

    def init_ui(self):
        self.setWindowTitle(f"Manage Ingredients for: {self.recipe_name}")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"Recipe: {self.recipe_name}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Splitter for two panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Available ingredients
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Available Ingredients:"))
        
        self.available_list = QListWidget()
        left_layout.addWidget(self.available_list)
        
        add_button = QPushButton("Add to Recipe →")
        add_button.clicked.connect(self.add_ingredient_to_recipe)
        left_layout.addWidget(add_button)
        
        splitter.addWidget(left_widget)

        # Right panel - Recipe ingredients
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Recipe Ingredients:"))
        
        self.recipe_ingredients_table = QTableWidget()
        self.recipe_ingredients_table.setColumnCount(3)
        self.recipe_ingredients_table.setHorizontalHeaderLabels(["Ingredient", "Quantity", "Unit"])
        right_layout.addWidget(self.recipe_ingredients_table)
        
        remove_button = QPushButton("← Remove from Recipe")
        remove_button.clicked.connect(self.remove_ingredient_from_recipe)
        right_layout.addWidget(remove_button)
        
        splitter.addWidget(right_widget)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_ingredients)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Load existing recipe ingredients
        self.load_recipe_ingredients()

    def load_available_ingredients(self):
        try:
            sheets_manager = self.parent().sheets_manager
            ingredients_data = sheets_manager.get_all_data("Ingredients")
            self.available_ingredients = ingredients_data
            
            self.available_list.clear()
            for ingredient in ingredients_data:
                item = QListWidgetItem(ingredient.get("Ingredient Name", ""))
                self.available_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load ingredients: {e}")

    def load_recipe_ingredients(self):
        try:
            sheets_manager = self.parent().sheets_manager
            recipe_ingredients_data = sheets_manager.get_all_data("Recipe_Ingredients")
            
            # Filter for current recipe
            current_recipe_ingredients = [
                ing for ing in recipe_ingredients_data 
                if ing.get("Recipe Name") == self.recipe_name
            ]
            
            self.recipe_ingredients = current_recipe_ingredients
            self.update_recipe_ingredients_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load recipe ingredients: {e}")

    def update_recipe_ingredients_table(self):
        self.recipe_ingredients_table.setRowCount(len(self.recipe_ingredients))
        
        for row, ingredient in enumerate(self.recipe_ingredients):
            self.recipe_ingredients_table.setItem(row, 0, QTableWidgetItem(ingredient.get("Ingredient Name", "")))
            self.recipe_ingredients_table.setItem(row, 1, QTableWidgetItem(str(ingredient.get("Quantity", ""))))
            self.recipe_ingredients_table.setItem(row, 2, QTableWidgetItem(ingredient.get("Unit (of ingredient, e.g., grams, ml)", "")))

    def add_ingredient_to_recipe(self):
        current_item = self.available_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an ingredient to add.")
            return

        ingredient_name = current_item.text()
        
        # Check if ingredient already in recipe
        for ing in self.recipe_ingredients:
            if ing.get("Ingredient Name") == ingredient_name:
                QMessageBox.warning(self, "Warning", "This ingredient is already in the recipe.")
                return

        # Get quantity and unit from user
        quantity, ok = self.get_quantity_input()
        if not ok:
            return

        unit, ok = self.get_unit_input()
        if not ok:
            return

        # Add to recipe ingredients
        new_ingredient = {
            "Recipe Name": self.recipe_name,
            "Ingredient Name": ingredient_name,
            "Quantity": quantity,
            "Unit (of ingredient, e.g., grams, ml)": unit
        }
        
        self.recipe_ingredients.append(new_ingredient)
        self.update_recipe_ingredients_table()

    def remove_ingredient_from_recipe(self):
        current_row = self.recipe_ingredients_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an ingredient to remove.")
            return

        reply = QMessageBox.question(self, "Confirm Remove", "Remove this ingredient from the recipe?")
        if reply == QMessageBox.Yes:
            del self.recipe_ingredients[current_row]
            self.update_recipe_ingredients_table()

    def get_quantity_input(self):
        from PySide6.QtWidgets import QInputDialog
        quantity, ok = QInputDialog.getDouble(self, "Quantity", "Enter quantity:", 0, 0, 10000, 2)
        return quantity, ok

    def get_unit_input(self):
        from PySide6.QtWidgets import QInputDialog
        units = ["grams", "ml", "pieces", "cups", "tablespoons", "teaspoons", "kg", "liters"]
        unit, ok = QInputDialog.getItem(self, "Unit", "Select unit:", units, 0, False)
        return unit, ok

    def save_ingredients(self):
        try:
            sheets_manager = self.parent().sheets_manager
            
            # Clear existing ingredients for this recipe
            sheets_manager.clear_recipe_ingredients(self.recipe_name)
            
            # Add all current ingredients
            for ingredient in self.recipe_ingredients:
                data_list = [
                    ingredient["Recipe Name"],
                    ingredient["Ingredient Name"],
                    ingredient["Quantity"],
                    ingredient["Unit (of ingredient, e.g., grams, ml)"]
                ]
                sheets_manager.add_row("Recipe_Ingredients", data_list)
            
            # Calculate and update recipe nutrition
            self.calculate_recipe_nutrition()
            
            QMessageBox.information(self, "Success", "Recipe ingredients saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save ingredients: {e}")

    def calculate_recipe_nutrition(self):
        try:
            sheets_manager = self.parent().sheets_manager
            
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            # Get ingredient nutritional data
            ingredients_data = sheets_manager.get_all_data("Ingredients")
            ingredient_nutrition = {ing["Ingredient Name"]: ing for ing in ingredients_data}
            
            # Calculate totals
            for recipe_ing in self.recipe_ingredients:
                ing_name = recipe_ing["Ingredient Name"]
                quantity = float(recipe_ing["Quantity"])
                
                if ing_name in ingredient_nutrition:
                    nutrition = ingredient_nutrition[ing_name]
                    
                    # Calculate per 100g and scale by quantity
                    scale_factor = quantity / 100.0
                    
                    total_calories += float(nutrition.get("Calories (per 100g)", 0)) * scale_factor
                    total_protein += float(nutrition.get("Protein (g per 100g)", 0)) * scale_factor
                    total_carbs += float(nutrition.get("Carbohydrates (g per 100g)", 0)) * scale_factor
                    total_fat += float(nutrition.get("Fat (g per 100g)", 0)) * scale_factor
            
            # Update recipe with calculated nutrition
            recipes_data = sheets_manager.get_all_data("Recipes")
            for i, recipe in enumerate(recipes_data):
                if recipe["Recipe Name"] == self.recipe_name:
                    # Update the recipe row
                    updated_data = [
                        recipe["Recipe Name"],
                        recipe["Instructions"],
                        recipe["Notes"],
                        round(total_calories, 2),
                        round(total_protein, 2),
                        round(total_carbs, 2),
                        round(total_fat, 2),
                        recipe["Portion Size (e.g., servings)"]
                    ]
                    sheets_manager.update_row("Recipes", i + 2, updated_data)
                    break
                    
        except Exception as e:
            print(f"Error calculating nutrition: {e}")

class RecipeDialog(QDialog):
    def __init__(self, parent=None, recipe_data=None):
        super().__init__(parent)
        self.recipe_data = recipe_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add/Edit Recipe")
        self.setModal(True)
        self.resize(500, 500)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.instructions_edit = QTextEdit()
        self.notes_edit = QTextEdit()
        self.portion_size_edit = QSpinBox()
        self.portion_size_edit.setMinimum(1)
        self.portion_size_edit.setMaximum(20)
        self.portion_size_edit.setValue(1)

        form_layout.addRow("Recipe Name:", self.name_edit)
        form_layout.addRow("Instructions:", self.instructions_edit)
        form_layout.addRow("Notes:", self.notes_edit)
        form_layout.addRow("Portion Size (servings):", self.portion_size_edit)

        layout.addLayout(form_layout)

        # Manage ingredients button
        self.manage_ingredients_btn = QPushButton("Manage Ingredients")
        self.manage_ingredients_btn.clicked.connect(self.manage_ingredients)
        layout.addWidget(self.manage_ingredients_btn)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Load data if editing
        if self.recipe_data:
            self.load_data()

    def load_data(self):
        self.name_edit.setText(self.recipe_data.get("Recipe Name", ""))
        self.instructions_edit.setPlainText(self.recipe_data.get("Instructions", ""))
        self.notes_edit.setPlainText(self.recipe_data.get("Notes", ""))
        portion_size = self.recipe_data.get("Portion Size (e.g., servings)", 1)
        try:
            self.portion_size_edit.setValue(int(float(portion_size)))
        except (ValueError, TypeError):
            self.portion_size_edit.setValue(1)

    def manage_ingredients(self):
        recipe_name = self.name_edit.text().strip()
        if not recipe_name:
            QMessageBox.warning(self, "Warning", "Please enter a recipe name first.")
            return

        dialog = RecipeIngredientsDialog(self.parent(), recipe_name)
        dialog.exec()

    def get_data(self):
        return {
            "Recipe Name": self.name_edit.text(),
            "Instructions": self.instructions_edit.toPlainText(),
            "Notes": self.notes_edit.toPlainText(),
            "Total Calories": 0,  # Will be calculated
            "Total Protein (g)": 0,  # Will be calculated
            "Total Carbohydrates (g)": 0,  # Will be calculated
            "Total Fat (g)": 0,  # Will be calculated
            "Portion Size (e.g., servings)": self.portion_size_edit.value()
        }

class IngredientDialog(QDialog):
    def __init__(self, parent=None, ingredient_data=None):
        super().__init__(parent)
        self.ingredient_data = ingredient_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add/Edit Ingredient")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.calories_edit = QDoubleSpinBox()
        self.calories_edit.setMaximum(9999.99)
        self.protein_edit = QDoubleSpinBox()
        self.protein_edit.setMaximum(999.99)
        self.carbs_edit = QDoubleSpinBox()
        self.carbs_edit.setMaximum(999.99)
        self.fat_edit = QDoubleSpinBox()
        self.fat_edit.setMaximum(999.99)
        self.unit_edit = QLineEdit()
        self.unit_edit.setText("grams")

        form_layout.addRow("Ingredient Name:", self.name_edit)
        form_layout.addRow("Calories (per 100g):", self.calories_edit)
        form_layout.addRow("Protein (g per 100g):", self.protein_edit)
        form_layout.addRow("Carbohydrates (g per 100g):", self.carbs_edit)
        form_layout.addRow("Fat (g per 100g):", self.fat_edit)
        form_layout.addRow("Unit:", self.unit_edit)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Load data if editing
        if self.ingredient_data:
            self.load_data()

    def load_data(self):
        self.name_edit.setText(self.ingredient_data.get("Ingredient Name", ""))
        try:
            self.calories_edit.setValue(float(self.ingredient_data.get("Calories (per 100g)", 0)))
            self.protein_edit.setValue(float(self.ingredient_data.get("Protein (g per 100g)", 0)))
            self.carbs_edit.setValue(float(self.ingredient_data.get("Carbohydrates (g per 100g)", 0)))
            self.fat_edit.setValue(float(self.ingredient_data.get("Fat (g per 100g)", 0)))
        except (ValueError, TypeError):
            pass
        self.unit_edit.setText(self.ingredient_data.get("Unit (e.g., grams, ml, piece)", "grams"))

    def get_data(self):
        return {
            "Ingredient Name": self.name_edit.text(),
            "Calories (per 100g)": self.calories_edit.value(),
            "Protein (g per 100g)": self.protein_edit.value(),
            "Carbohydrates (g per 100g)": self.carbs_edit.value(),
            "Fat (g per 100g)": self.fat_edit.value(),
            "Unit (e.g., grams, ml, piece)": self.unit_edit.text()
        }

class NutritionChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_daily_nutrition(self, date_str, calories, protein, carbs, fat):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Create bar chart
        nutrients = ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)']
        values = [calories, protein, carbs, fat]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        bars = ax.bar(nutrients, values, color=colors)
        ax.set_title(f'Daily Nutrition - {date_str}')
        ax.set_ylabel('Amount')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value:.1f}', ha='center', va='bottom')
        
        self.fig.tight_layout()
        self.draw()

class NutritionMealPlannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.sheets_manager = GoogleSheetsManager()
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Nutrition Meal Planner")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)

        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create header
        self.create_header(main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_recipes_tab()
        self.create_ingredients_tab()
        self.create_meal_plan_tab()
        self.create_dashboard_tab()

        # Create menu bar and status bar
        self.create_menu_bar()
        self.create_status_bar()

        # Apply theme
        self.apply_theme()

        # Load initial data
        self.refresh_all_data()

    def create_header(self, parent_layout):
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("Nutrition Meal Planner")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.theme_button = QPushButton("🌙 Switch to Light Mode")
        self.theme_button.setMinimumHeight(35)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.refresh_button = QPushButton("🔄 Refresh Data")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.refresh_all_data)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.theme_button)

        parent_layout.addWidget(header_frame)

    def create_recipes_tab(self):
        recipes_widget = QWidget()
        layout = QVBoxLayout(recipes_widget)

        # Buttons
        button_layout = QHBoxLayout()
        add_recipe_btn = QPushButton("Add Recipe")
        edit_recipe_btn = QPushButton("Edit Recipe")
        delete_recipe_btn = QPushButton("Delete Recipe")
        manage_ingredients_btn = QPushButton("Manage Ingredients")

        add_recipe_btn.clicked.connect(self.add_recipe)
        edit_recipe_btn.clicked.connect(self.edit_recipe)
        delete_recipe_btn.clicked.connect(self.delete_recipe)
        manage_ingredients_btn.clicked.connect(self.manage_recipe_ingredients)

        button_layout.addWidget(add_recipe_btn)
        button_layout.addWidget(edit_recipe_btn)
        button_layout.addWidget(delete_recipe_btn)
        button_layout.addWidget(manage_ingredients_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table
        self.recipes_table = QTableWidget()
        layout.addWidget(self.recipes_table)

        self.tab_widget.addTab(recipes_widget, "Recipes")

    def create_ingredients_tab(self):
        ingredients_widget = QWidget()
        layout = QVBoxLayout(ingredients_widget)

        # Buttons
        button_layout = QHBoxLayout()
        add_ingredient_btn = QPushButton("Add Ingredient")
        edit_ingredient_btn = QPushButton("Edit Ingredient")
        delete_ingredient_btn = QPushButton("Delete Ingredient")

        add_ingredient_btn.clicked.connect(self.add_ingredient)
        edit_ingredient_btn.clicked.connect(self.edit_ingredient)
        delete_ingredient_btn.clicked.connect(self.delete_ingredient)

        button_layout.addWidget(add_ingredient_btn)
        button_layout.addWidget(edit_ingredient_btn)
        button_layout.addWidget(delete_ingredient_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table
        self.ingredients_table = QTableWidget()
        layout.addWidget(self.ingredients_table)

        self.tab_widget.addTab(ingredients_widget, "Ingredients")

    def create_meal_plan_tab(self):
        meal_plan_widget = QWidget()
        layout = QHBoxLayout(meal_plan_widget)

        # Left side - Calendar
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("Select Date:"))
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.calendar_date_changed)
        left_layout.addWidget(self.calendar)

        # Meal plan buttons
        meal_buttons_layout = QVBoxLayout()
        add_meal_btn = QPushButton("Add Meal")
        edit_meal_btn = QPushButton("Edit Meal")
        delete_meal_btn = QPushButton("Delete Meal")

        add_meal_btn.clicked.connect(self.add_meal_plan)
        edit_meal_btn.clicked.connect(self.edit_meal_plan)
        delete_meal_btn.clicked.connect(self.delete_meal_plan)

        meal_buttons_layout.addWidget(add_meal_btn)
        meal_buttons_layout.addWidget(edit_meal_btn)
        meal_buttons_layout.addWidget(delete_meal_btn)
        meal_buttons_layout.addStretch()

        left_layout.addLayout(meal_buttons_layout)
        layout.addWidget(left_widget)

        # Right side - Meal plan table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.selected_date_label = QLabel("Meals for: Today")
        right_layout.addWidget(self.selected_date_label)
        
        self.meal_plan_table = QTableWidget()
        right_layout.addWidget(self.meal_plan_table)
        
        layout.addWidget(right_widget)

        self.tab_widget.addTab(meal_plan_widget, "Meal Plan")

    def create_dashboard_tab(self):
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)

        # Date selection for dashboard
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("View nutrition for:"))
        self.dashboard_date_edit = QDateEdit()
        self.dashboard_date_edit.setDate(QDate.currentDate())
        self.dashboard_date_edit.dateChanged.connect(self.update_dashboard)
        date_layout.addWidget(self.dashboard_date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Nutrition chart
        self.nutrition_chart = NutritionChart(self, width=8, height=6, dpi=100)
        layout.addWidget(self.nutrition_chart)

        self.tab_widget.addTab(dashboard_widget, "Dashboard")

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Refresh Data', self.refresh_all_data)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)

        # View menu
        view_menu = menubar.addMenu('View')
        theme_action = QAction('Toggle Theme', self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Connected to Google Sheets")

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
            self.theme_button.setText("☀️ Switch to Light Mode")
            self.status_bar.showMessage("Ready - Dark theme active")
        else:
            self.setStyleSheet("")
            self.theme_button.setText("🌙 Switch to Dark Mode")
            self.status_bar.showMessage("Ready - Light theme active")

    def refresh_all_data(self):
        self.load_recipes_data()
        self.load_ingredients_data()
        self.load_meal_plan_data()
        self.update_dashboard()
        self.status_bar.showMessage("Data refreshed from Google Sheets", 3000)

    def load_recipes_data(self):
        try:
            recipes_data = self.sheets_manager.get_all_data("Recipes")
            self.populate_table(self.recipes_table, recipes_data)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load recipes data: {e}")

    def load_ingredients_data(self):
        try:
            ingredients_data = self.sheets_manager.get_all_data("Ingredients")
            self.populate_table(self.ingredients_table, ingredients_data)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load ingredients data: {e}")

    def load_meal_plan_data(self):
        try:
            selected_date = self.calendar.selectedDate().toPython()
            date_str = selected_date.strftime('%Y-%m-%d')
            
            meal_plan_data = self.sheets_manager.get_all_data("Meal_Plan")
            
            # Filter for selected date
            daily_meals = [meal for meal in meal_plan_data if meal.get("Date") == date_str]
            
            self.populate_table(self.meal_plan_table, daily_meals)
            self.selected_date_label.setText(f"Meals for: {selected_date.strftime('%A, %B %d, %Y')}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load meal plan data: {e}")

    def calendar_date_changed(self):
        self.load_meal_plan_data()

    def populate_table(self, table, data):
        if not data:
            table.setRowCount(0)
            table.setColumnCount(0)
            return

        # Set up table
        table.setRowCount(len(data))
        table.setColumnCount(len(data[0]))
        table.setHorizontalHeaderLabels(list(data[0].keys()))

        # Populate data
        for row_idx, row_data in enumerate(data):
            for col_idx, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)

        # Resize columns
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()

    def add_recipe(self):
        dialog = RecipeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            recipe_data = dialog.get_data()
            data_list = list(recipe_data.values())
            if self.sheets_manager.add_row("Recipes", data_list):
                self.load_recipes_data()
                QMessageBox.information(self, "Success", "Recipe added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add recipe.")

    def edit_recipe(self):
        current_row = self.recipes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a recipe to edit.")
            return

        # Get current recipe data
        recipe_data = {}
        for col in range(self.recipes_table.columnCount()):
            header = self.recipes_table.horizontalHeaderItem(col).text()
            item = self.recipes_table.item(current_row, col)
            recipe_data[header] = item.text() if item else ""

        dialog = RecipeDialog(self, recipe_data)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            data_list = list(updated_data.values())
            if self.sheets_manager.update_row("Recipes", current_row + 2, data_list):
                self.load_recipes_data()
                QMessageBox.information(self, "Success", "Recipe updated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to update recipe.")

    def delete_recipe(self):
        current_row = self.recipes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a recipe to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this recipe?")
        if reply == QMessageBox.Yes:
            if self.sheets_manager.delete_row("Recipes", current_row + 2):
                self.load_recipes_data()
                QMessageBox.information(self, "Success", "Recipe deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete recipe.")

    def manage_recipe_ingredients(self):
        current_row = self.recipes_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a recipe to manage ingredients.")
            return

        # Get recipe name
        recipe_name_item = self.recipes_table.item(current_row, 0)  # Assuming first column is recipe name
        if not recipe_name_item:
            QMessageBox.warning(self, "Warning", "Could not get recipe name.")
            return

        recipe_name = recipe_name_item.text()
        dialog = RecipeIngredientsDialog(self, recipe_name)
        if dialog.exec() == QDialog.Accepted:
            self.load_recipes_data()  # Refresh to show updated nutrition values

    def add_ingredient(self):
        dialog = IngredientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            ingredient_data = dialog.get_data()
            data_list = list(ingredient_data.values())
            if self.sheets_manager.add_row("Ingredients", data_list):
                self.load_ingredients_data()
                QMessageBox.information(self, "Success", "Ingredient added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add ingredient.")

    def edit_ingredient(self):
        current_row = self.ingredients_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an ingredient to edit.")
            return

        # Get current ingredient data
        ingredient_data = {}
        for col in range(self.ingredients_table.columnCount()):
            header = self.ingredients_table.horizontalHeaderItem(col).text()
            item = self.ingredients_table.item(current_row, col)
            ingredient_data[header] = item.text() if item else ""

        dialog = IngredientDialog(self, ingredient_data)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            data_list = list(updated_data.values())
            if self.sheets_manager.update_row("Ingredients", current_row + 2, data_list):
                self.load_ingredients_data()
                QMessageBox.information(self, "Success", "Ingredient updated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to update ingredient.")

    def delete_ingredient(self):
        current_row = self.ingredients_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an ingredient to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this ingredient?")
        if reply == QMessageBox.Yes:
            if self.sheets_manager.delete_row("Ingredients", current_row + 2):
                self.load_ingredients_data()
                QMessageBox.information(self, "Success", "Ingredient deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete ingredient.")

    def add_meal_plan(self):
        selected_date = self.calendar.selectedDate().toPython()
        dialog = MealPlanDialog(self, selected_date)
        if dialog.exec() == QDialog.Accepted:
            meal_data = dialog.get_data()
            data_list = list(meal_data.values())
            if self.sheets_manager.add_row("Meal_Plan", data_list):
                self.load_meal_plan_data()
                self.update_dashboard()
                QMessageBox.information(self, "Success", "Meal added to plan successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add meal to plan.")

    def edit_meal_plan(self):
        current_row = self.meal_plan_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a meal to edit.")
            return

        # Get current meal data
        meal_data = {}
        for col in range(self.meal_plan_table.columnCount()):
            header = self.meal_plan_table.horizontalHeaderItem(col).text()
            item = self.meal_plan_table.item(current_row, col)
            meal_data[header] = item.text() if item else ""

        selected_date = self.calendar.selectedDate().toPython()
        dialog = MealPlanDialog(self, selected_date, meal_data)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            data_list = list(updated_data.values())
            
            # Find the actual row in the full meal plan data
            meal_plan_data = self.sheets_manager.get_all_data("Meal_Plan")
            for i, meal in enumerate(meal_plan_data):
                if (meal.get("Date") == meal_data.get("Date") and 
                    meal.get("Meal Type") == meal_data.get("Meal Type") and
                    meal.get("Recipe Name") == meal_data.get("Recipe Name")):
                    if self.sheets_manager.update_row("Meal_Plan", i + 2, data_list):
                        self.load_meal_plan_data()
                        self.update_dashboard()
                        QMessageBox.information(self, "Success", "Meal updated successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update meal.")
                    break

    def delete_meal_plan(self):
        current_row = self.meal_plan_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a meal to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this meal?")
        if reply == QMessageBox.Yes:
            # Get current meal data
            meal_data = {}
            for col in range(self.meal_plan_table.columnCount()):
                header = self.meal_plan_table.horizontalHeaderItem(col).text()
                item = self.meal_plan_table.item(current_row, col)
                meal_data[header] = item.text() if item else ""

            # Find the actual row in the full meal plan data
            meal_plan_data = self.sheets_manager.get_all_data("Meal_Plan")
            for i, meal in enumerate(meal_plan_data):
                if (meal.get("Date") == meal_data.get("Date") and 
                    meal.get("Meal Type") == meal_data.get("Meal Type") and
                    meal.get("Recipe Name") == meal_data.get("Recipe Name")):
                    if self.sheets_manager.delete_row("Meal_Plan", i + 2):
                        self.load_meal_plan_data()
                        self.update_dashboard()
                        QMessageBox.information(self, "Success", "Meal deleted successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to delete meal.")
                    break

    def update_dashboard(self):
        try:
            selected_date = self.dashboard_date_edit.date().toPython()
            date_str = selected_date.strftime('%Y-%m-%d')
            
            # Get meal plan for the selected date
            meal_plan_data = self.sheets_manager.get_all_data("Meal_Plan")
            daily_meals = [meal for meal in meal_plan_data if meal.get("Date") == date_str]
            
            # Get recipes data
            recipes_data = self.sheets_manager.get_all_data("Recipes")
            recipes_dict = {recipe["Recipe Name"]: recipe for recipe in recipes_data}
            
            # Calculate daily totals
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for meal in daily_meals:
                recipe_name = meal.get("Recipe Name")
                portion_size = float(meal.get("Portion Size (for the meal plan, referring to the recipe's portion size)", 1.0))
                
                if recipe_name in recipes_dict:
                    recipe = recipes_dict[recipe_name]
                    recipe_portions = float(recipe.get("Portion Size (e.g., servings)", 1))
                    
                    # Calculate nutrition per portion and scale by meal portion size
                    scale_factor = portion_size / recipe_portions
                    
                    total_calories += float(recipe.get("Total Calories", 0)) * scale_factor
                    total_protein += float(recipe.get("Total Protein (g)", 0)) * scale_factor
                    total_carbs += float(recipe.get("Total Carbohydrates (g)", 0)) * scale_factor
                    total_fat += float(recipe.get("Total Fat (g)", 0)) * scale_factor
            
            # Update chart
            self.nutrition_chart.plot_daily_nutrition(date_str, total_calories, total_protein, total_carbs, total_fat)
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def show_about(self):
        QMessageBox.about(self, "About", "Nutrition Meal Planner v1.0\n\nA desktop application for managing recipes, ingredients, and meal planning with Google Sheets integration.")

def main():
    app = QApplication(sys.argv)



    window = NutritionMealPlannerApp()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

