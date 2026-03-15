---
version: "1.0.0"
---

# Meal Planner

A personalized meal planning CLI tool with nutritional analysis and smart shopping lists.

## Description

Meal Planner creates customized meal plans based on your personal profile, dietary goals, and restrictions. It calculates nutritional requirements, recommends appropriate recipes, and generates shopping lists automatically—making healthy eating effortless.

## Features

- 👤 **Personal Nutrition Profile**: Calculate nutritional needs based on age, weight, height, and activity level
- 🍽️ **Smart Recipe Recommendations**: AI-powered suggestions aligned with your goals
- 📊 **Nutritional Analysis**: Automatic calculation of calories, protein, carbs, and fats per meal
- 📅 **Weekly/Monthly Planning**: Generate complete meal plans for multiple days
- 🛒 **Intelligent Shopping Lists**: Auto-generated grocery lists from your meal plan

## Installation

```bash
# Add to PATH
ln -s ~/.openclaw/workspace/skills/meal-planner/meal-planner ~/.local/bin/meal-planner
```

## Usage

### Create Your Profile

```bash
# Basic profile
meal-planner profile-create \
  --name "John" \
  --age 30 \
  --gender male \
  --weight 70 \
  --height 175 \
  --goal lose

# Complete profile with dietary restrictions and allergies
meal-planner profile-create \
  --name "Jane" \
  --age 25 \
  --gender female \
  --weight 55 \
  --height 160 \
  --activity moderate \
  --goal maintain \
  --restrictions vegetarian \
  --allergies peanuts shellfish
```

### Activity Levels

| Level | Description |
|-------|-------------|
| `sedentary` | Desk job, minimal exercise |
| `light` | Light activity (1-2 workout days/week) |
| `moderate` | Moderate activity (3-5 workout days/week) |
| `active` | High activity (6-7 workout days/week) |
| `very_active` | Very high activity (manual labor/athlete) |

### Fitness Goals

| Goal | Calorie Adjustment |
|------|-------------------|
| `lose` | Fat loss (-500 kcal/day) |
| `maintain` | Maintenance (baseline) |
| `gain` | Muscle gain (+500 kcal/day) |

### Generate Meal Plans

```bash
# Generate 7-day plan (default)
meal-planner plan-generate

# Generate 14-day plan
meal-planner plan-generate --days 14
```

### View Your Plan

```bash
# View today's plan
meal-planner plan-show

# View specific date
meal-planner plan-show --date 2024-01-15
```

### Shopping Lists

```bash
# Generate shopping list for next 7 days
meal-planner shopping-list

# Generate for next 14 days
meal-planner shopping-list --days 14
```

### Nutritional Information

```bash
# Query a specific food
meal-planner nutrition "chicken breast"

# Fuzzy search
meal-planner nutrition chicken
```

## Built-in Food Database

The tool includes nutritional data for common foods across categories:

**Grains & Carbs**
- Rice, noodles, steamed buns, oats, sweet potato, corn, whole wheat bread

**Proteins**
- Chicken breast, eggs, beef, salmon, tofu, milk, shrimp

**Vegetables**
- Broccoli, spinach, carrots, tomato, cucumber, bell pepper, lettuce, celery

**Fruits**
- Apple, banana, orange, blueberry, kiwi

**Nuts & Oils**
- Almonds, walnuts, olive oil

## Data Storage

Data is stored in `~/.openclaw/data/meal-planner/`:
- `meal_planner.db` - SQLite database

## Examples

### Quick Start

```bash
# 1. Create your profile
meal-planner profile-create \
  --name "Alex" \
  --age 28 \
  --gender male \
  --weight 75 \
  --height 180 \
  --activity moderate \
  --goal maintain

# 2. Generate a weekly meal plan
meal-planner plan-generate

# 3. Check today's meals
meal-planner plan-show

# 4. Get your shopping list
meal-planner shopping-list
```

### Vegetarian Meal Planning

```bash
meal-planner profile-create \
  --name "Vegetarian User" \
  --age 30 \
  --gender female \
  --weight 58 \
  --height 165 \
  --activity light \
  --goal maintain \
  --restrictions vegetarian \
  --allergies nuts

meal-planner plan-generate --days 7
```

## Technical Details

- **Language**: Python 3.8+
- **Database**: SQLite
- **CLI Framework**: argparse
- **Nutrition Algorithm**: Mifflin-St Jeor equation for BMR calculation

## Requirements

- Python 3.8 or higher
- SQLite3
- Terminal access

## License

MIT License