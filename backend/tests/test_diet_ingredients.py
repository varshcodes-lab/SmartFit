from services.diet_engine import select_meals

def test_selected_four_meals_have_ingredient_quantities_and_summed_macros():
    meals = select_meals("vegetarian", [], 2200)
    assert len(meals) == 4
    for meal in meals:
        assert meal.get("ingredients"), f"Missing ingredient details for {meal.get('name')}"
        for item in meal["ingredients"]:
            assert item["quantity"] > 0 and item["unit"]
        for field in ("kcal", "protein", "carbs", "fat"):
            assert meal[field] == round(sum(i[field] for i in meal["ingredients"]))

def test_ingredient_list_has_metric_weights_or_volumes():
    meals = select_meals("vegetarian", [], 2200)
    items = [i for meal in meals for i in meal.get("ingredients", [])]
    assert any(i["grams"] is not None for i in items)
    assert any(i["millilitres"] is not None for i in items)
    assert all("practical_portion" in i for i in items)

def test_peanut_allergy_does_not_return_peanuts_in_selected_ingredients():
    meals = select_meals("vegetarian", ["peanuts"], 2200)
    names = [i["name"].lower() for m in meals for i in m.get("ingredients", [])]
    assert not any("peanut" in name for name in names)
