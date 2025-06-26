# Quick Start Guide - Nutrition Meal Planner

## 🚀 Get Started in 5 Minutes

### Step 1: Download Your Service Account Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account with Editor role
5. Download the JSON key file
6. **Rename it to `service_account_key.json`**
7. **Place it in the same folder as this application**

### Step 2: Run Setup
```bash
python3 setup.py
```

This will:
- Check your Python version
- Install all required packages
- Verify your Google Sheets connection
- Run tests to ensure everything works

### Step 3: Launch the Application
```bash
python3 nutrition_meal_planner_final.py
```

## 📱 First Time Usage

### 1. Add Some Ingredients
- Go to the **Ingredients** tab
- Click **Add Ingredient**
- Add common ingredients like:
  - Chicken Breast (165 cal, 31g protein, 0g carbs, 3.6g fat per 100g)
  - Rice (130 cal, 2.7g protein, 28g carbs, 0.3g fat per 100g)
  - Broccoli (34 cal, 2.8g protein, 7g carbs, 0.4g fat per 100g)

### 2. Create Your First Recipe
- Go to the **Recipes** tab
- Click **Add Recipe**
- Enter recipe name and instructions
- Click **Manage Ingredients** to add ingredients with quantities
- The app will automatically calculate nutrition!

### 3. Plan Your Meals
- Go to the **Meal Plan** tab
- Select a date on the calendar
- Click **Add Meal**
- Choose meal type and recipe
- Set portion size

### 4. View Your Nutrition
- Go to the **Dashboard** tab
- Select any date to see nutrition breakdown
- View colorful charts of your daily macros!

## 🔧 Troubleshooting

**Can't connect to Google Sheets?**
- Make sure `service_account_key.json` is in the right place
- Check that you've shared the spreadsheet with your service account email
- Verify APIs are enabled in Google Cloud Console

**Application won't start?**
- Run `python3 test_app.py` to diagnose issues
- Check that you have Python 3.11+
- Install missing dependencies with `pip install -r requirements.txt`

## 💡 Pro Tips

1. **Batch Add Ingredients**: Add all your common ingredients first
2. **Use Realistic Portions**: Set recipe portions to match how you actually eat
3. **Plan Weekly**: Use the calendar to plan a full week of meals
4. **Check Daily Totals**: Use the dashboard to track your nutrition goals
5. **Data is Synced**: Your data is automatically saved to Google Sheets - access from anywhere!

## 🎯 What's Next?

- Build a library of your favorite recipes
- Track your nutrition trends over time
- Share meal plans with family members
- Use Google Sheets for advanced analysis

**Need help?** Check the full README.md for detailed documentation.

**Happy meal planning! 🍽️**

