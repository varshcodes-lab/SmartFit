import pytest
from services.diet_engine import calculate_targets, select_meals, build_diet_plan

def p(**kw):
 d={'age':25,'sex':'unspecified','height_cm':170,'weight_kg':70,'activity_level':'moderate','goal':'muscle_gain','dietary_preference':'vegetarian','allergies':[]}; d.update(kw); return d

def test_targets_positive():
 t=calculate_targets(p()); assert t['daily_calories_kcal']>0 and t['protein_g']>0 and t['fat_g']>0

def test_weight_loss_lower_than_gain():
 assert calculate_targets(p(goal='weight_loss'))['daily_calories_kcal'] < calculate_targets(p(goal='muscle_gain'))['daily_calories_kcal']

@pytest.mark.parametrize('diet,forbidden',[('vegan',['milk','curd','paneer','yogurt','eggs','chicken','fish']),('vegetarian',['chicken','fish']),('non-vegetarian',[])])
def test_diet_filter(diet,forbidden):
 meals=select_meals(diet,[],2200); assert len(meals)==4
 for m in meals: assert not any(x in m['name'].lower() for x in forbidden)

def test_allergy_filter():
 meals=select_meals('vegetarian',['peanuts'],2200); assert all('peanut' not in m['name'].lower() and 'peanuts' not in m['tags'] for m in meals)

def test_plan_shape():
 r=build_diet_plan(p()); assert {'targets','meals','explanation','sources','disclaimer'} <= r.keys() and len(r['meals'])==4
