# Problem Statement

Select a set of seed users within budget constraints to maximize influence spread through a social network. Users become activated when incoming influence from already-activated neighbors meets their activation threshold, creating a cascade effect. The objective combines reach (activated users), key user activation bonus, and cost efficiency.

## Instance Data

```python
{
  "users": [
    {"id": "u1", "cost": 250, "category": "influencer", "activation_threshold": 10},
    {"id": "u2", "cost": 80, "category": "regular", "activation_threshold": 60},
    {"id": "u3", "cost": 70, "category": "regular", "activation_threshold": 90},
    {"id": "u4", "cost": 150, "category": "expert", "activation_threshold": 100},
    {"id": "u5", "cost": 90, "category": "regular", "activation_threshold": 70},
    {"id": "u6", "cost": 200, "category": "influencer", "activation_threshold": 120},
    {"id": "u7", "cost": 300, "category": "influencer", "activation_threshold": 10},
    {"id": "u8", "cost": 110, "category": "regular", "activation_threshold": 40},
    {"id": "u9", "cost": 60, "category": "regular", "activation_threshold": 80},
    {"id": "u10", "cost": 220, "category": "expert", "activation_threshold": 150},
    {"id": "u11", "cost": 50, "category": "regular", "activation_threshold": 50},
    {"id": "u12", "cost": 130, "category": "regular", "activation_threshold": 90},
    {"id": "u13", "cost": 280, "category": "influencer", "activation_threshold": 10},
    {"id": "u14", "cost": 85, "category": "regular", "activation_threshold": 60},
    {"id": "u15", "cost": 180, "category": "expert", "activation_threshold": 10},
    {"id": "u16", "cost": 95, "category": "regular", "activation_threshold": 50},
    {"id": "u17", "cost": 40, "category": "regular", "activation_threshold": 100},
    {"id": "u18", "cost": 190, "category": "expert", "activation_threshold": 110},
    {"id": "u19", "cost": 210, "category": "influencer", "activation_threshold": 130},
    {"id": "u20", "cost": 75, "category": "regular", "activation_threshold": 70},
    {"id": "u21", "cost": 100, "category": "expert", "activation_threshold": 80},
    {"id": "u22", "cost": 120, "category": "regular", "activation_threshold": 10},
    {"id": "u23", "cost": 140, "category": "regular", "activation_threshold": 120},
    {"id": "u24", "cost": 160, "category": "expert", "activation_threshold": 90},
    {"id": "u25", "cost": 240, "category": "influencer", "activation_threshold": 10}
  ],
  "connections": [
    {"from": "u1", "to": "u2", "strength": 70},
    {"from": "u1", "to": "u5", "strength": 50},
    {"from": "u7", "to": "u8", "strength": 50},
    {"from": "u7", "to": "u9", "strength": 30},
    {"from": "u15", "to": "u16", "strength": 60},
    {"from": "u22", "to": "u5", "strength": 30},
    {"from": "u2", "to": "u3", "strength": 40},
    {"from": "u8", "to": "u3", "strength": 50},
    {"from": "u8", "to": "u9", "strength": 60}
  ],
  "budget": {"total": 1000, "influencer": 600},
  "max_seeds": 5,
  "required_seed_category": "expert"
}
```

## Constraints

1. **Total cost** of selected seeds must not exceed the budget (1000)
2. **Maximum seeds**: Select at most 5 users as initial seeds
3. **Cascade activation**: A user becomes activated if:
   - They are selected as a seed, OR
   - The sum of influence strengths from already-activated neighbors meets or exceeds their activation threshold
4. **Key user**: The first user with category "expert" (u4) serves as the key user for bonus scoring

## Objective

Find a solution that **maximizes** the composite score:
- 10 points per activated user
- 50 points if the key user (u4) is activated

**Expected optimal solution**: Maximum score with total_cost=1000 (uses full budget)

## Output Format

```json
{
  "selected_seeds": ["u1", "u5"],
  "activated_users": ["u1", "u2", "u3", "u5"],
  "total_cost": 340,
  "total_activated_count": 4,
  "key_user_activated": true,
  "final_score": 95
}
```

### Field Descriptions

- `selected_seeds`: Array of user IDs chosen as seeds
- `activated_users`: Array of all activated user IDs (seeds + cascade)
- `total_cost`: Integer, total cost of selected seeds
- `total_activated_count`: Integer, count of activated users
- `key_user_activated`: Boolean, whether key user (u4) was activated
- `final_score`: Integer, composite score value
