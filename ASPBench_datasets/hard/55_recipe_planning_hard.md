# Problem Statement

Plan the cooking of 4 recipes with shared resources, optimizing for minimal total time while respecting resource constraints and inter-recipe dependencies.

## Instance Data

**4 Recipes with Steps:**

- **Roast Chicken:**
  - prep_chicken: 15 min, uses prep_area
  - bake_chicken: 50 min, uses oven
  - rest_chicken: 10 min, uses prep_area

- **Vegetable Soup:**
  - chop_veg_soup: 20 min, uses prep_area
  - simmer_stock: 30 min, uses stove

- **Risotto:**
  - chop_onion: 5 min, uses prep_area
  - cook_risotto: 25 min, uses stove

- **Side Salad:**
  - wash_greens: 5 min, uses prep_area
  - mix_dressing: 10 min, uses prep_area

**Step Precedences (within each recipe):**

- Roast Chicken: prep_chicken → bake_chicken → rest_chicken
- Vegetable Soup: chop_veg_soup → simmer_stock
- Risotto: chop_onion → cook_risotto
- Side Salad: wash_greens → mix_dressing

**Inter-Recipe Dependency:**

- The vegetable_soup's simmer_stock step produces veggie_stock, which is **required** by risotto's cook_risotto step (simmer_stock must finish before cook_risotto starts)

**Shared Resources:**

- **prep_area:** Capacity 2 (can be used by two tasks simultaneously)
- **oven:** Capacity 1, requires a 10-minute preheat task before any baking
- **stove:** Capacity 1

**Special Tasks:**

- preheat_oven: 10 min, uses oven (must complete before any baking)

## Constraints

1. **All required recipe steps** must be completed
2. **Step precedences** within each recipe must be respected
3. **Inter-recipe dependency:** simmer_stock must finish before cook_risotto starts
4. **Resource capacity:** prep_area can handle 2 concurrent tasks, oven and stove handle 1 task each
5. **Oven preheating:** preheat_oven must complete before any bake_chicken step starts
6. **Task timing:** Each task must run for its specified duration using the correct resource

## Objective

Minimize the total time (makespan) to complete all recipes.

**Expected optimal value:** total_time=75

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "total_time": 75,
  "schedule": [
    {
      "recipe": "roast_chicken",
      "step": "prep_chicken",
      "start_time": 0,
      "end_time": 15,
      "resource": "prep_area"
    },
    {
      "task": "preheat_oven",
      "start_time": 5,
      "end_time": 15,
      "resource": "oven"
    }
  ],
  "feasible": true
}
```

**Field Descriptions:**
- `total_time`: The makespan (latest end_time across all tasks)
- `schedule`: List of all tasks with their timing and resource allocation
- Recipe tasks include: `recipe`, `step`, `start_time`, `end_time`, `resource`
- Special tasks include: `task`, `start_time`, `end_time`, `resource`
- `feasible`: Boolean indicating if solution is valid
