# Nutrition Meal Planner

A comprehensive desktop application for managing recipes, ingredients, meal planning, and nutrition tracking with Google Sheets integration for real-time data synchronization across devices.

## Features

- **Recipe Management**: Create, edit, and manage recipes with detailed ingredient lists
- **Ingredient Database**: Maintain a comprehensive database of ingredients with nutritional information
- **Meal Calendar**: Plan meals using an interactive calendar interface
- **Nutrition Dashboard**: Visualize daily and weekly macro nutrition with charts
- **Google Sheets Integration**: All data is synchronized with Google Sheets for access from any device
- **Dark/Light Theme**: Toggle between dark and light themes for comfortable viewing
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## Requirements

- Python 3.11 or higher
- Google Cloud Project with Sheets API and Drive API enabled
- Service Account credentials for Google Sheets access

## Installation

### 1. Install Python Dependencies

```bash
pip install PySide6 gspread qdarkstyle matplotlib pandas
```

### 2. Set up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in the details and create
   - Add the "Editor" role to the service account
   - Create a JSON key for the service account
5. Download the JSON key file and rename it to `service_account_key.json`
6. Place the `service_account_key.json` file in the same directory as the application

### 3. Set up Google Sheets Database

The application will automatically create a Google Sheet named "Nutrition Meal Planner Database" with the following worksheets:

- **Recipes**: Store recipe information with calculated nutrition
- **Ingredients**: Database of ingredients with nutritional values per 100g
- **Recipe_Ingredients**: Links recipes to their ingredients with quantities
- **Meal_Plan**: Calendar-based meal planning data

Make sure to share the created spreadsheet with your service account email address (found in the JSON key file).

## Usage

### Running the Application

```bash
python3 nutrition_meal_planner_final.py
```

### Application Tabs

#### 1. Recipes Tab
- Add new recipes with instructions and notes
- Edit existing recipes
- Manage ingredients for each recipe
- View calculated nutritional information

#### 2. Ingredients Tab
- Add ingredients with nutritional information (per 100g)
- Edit ingredient details
- Maintain a comprehensive ingredient database

#### 3. Meal Plan Tab
- Use the calendar to select dates
- Add meals to specific dates
- Edit or delete planned meals
- View daily meal schedules

#### 4. Dashboard Tab
- Select a date to view nutrition summary
- Visual charts showing daily calories, protein, carbs, and fat
- Real-time calculation based on planned meals

### Key Features

#### Recipe Management
- Create recipes with detailed instructions
- Add ingredients with specific quantities
- Automatic calculation of total nutrition per recipe
- Portion size management

#### Meal Planning
- Calendar-based interface for meal planning
- Support for multiple meal types (Breakfast, Lunch, Dinner, Snack)
- Flexible portion sizing for meal plans

#### Nutrition Tracking
- Automatic calculation of daily nutrition totals
- Visual charts for easy understanding
- Historical data tracking through Google Sheets

## File Structure

```
nutrition-meal-planner/
├── nutrition_meal_planner_final.py    # Main application file
├── service_account_key.json           # Google Sheets API credentials
├── test_app.py                        # Test script
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Google Sheets Connection Error**
   - Verify that the `service_account_key.json` file is in the correct location
   - Ensure the Google Sheets API and Drive API are enabled
   - Check that the spreadsheet is shared with the service account email

2. **Qt Platform Plugin Error**
   - On Linux, install required X11 libraries:
     ```bash
     sudo apt-get install libxcb-cursor0 libxcb-xinerama0 libxcb-randr0 libxcb-render-util0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-shape0
     ```

3. **Import Errors**
   - Ensure all required Python packages are installed
   - Use Python 3.11 or higher

### Testing the Application

Run the test script to verify everything is working:

```bash
python3 test_app.py
```

## Data Synchronization

All data is automatically synchronized with Google Sheets, allowing you to:

- Access your data from multiple devices
- Share meal plans with family members
- Backup your nutrition data in the cloud
- Use Google Sheets for additional analysis or reporting

## Customization

### Adding New Meal Types
Edit the `MealPlanDialog` class to add custom meal types to the dropdown.

### Modifying Nutrition Charts
The `NutritionChart` class can be customized to show different visualizations or additional metrics.

### Theme Customization
The application supports both dark and light themes. You can modify the theme switching logic in the `apply_theme` method.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Google Sheets API setup
3. Run the test script to identify specific problems

## License

This application is provided as-is for personal use. Please ensure compliance with Google's API terms of service when using the Google Sheets integration.

## Version History

- **v1.0** - Initial release with full functionality
  - Recipe management with ingredient tracking
  - Meal calendar planning
  - Nutrition dashboard with charts
  - Google Sheets integration
  - Dark/light theme support

