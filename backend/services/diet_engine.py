import re
"""Rule-based nutrition targets and diet-compatible meal selection; Groq is explanation-only."""
import os, json, urllib.request

ACTIVITY={"sedentary":1.2,"light":1.375,"moderate":1.55,"very_active":1.725,"extra_active":1.9}
ADJUST={"muscle_gain":250,"strength":100,"general_fitness":0,"weight_loss":-350}
PROTEIN={"muscle_gain":1.8,"strength":1.7,"general_fitness":1.4,"weight_loss":1.8}
# Values are approximate example servings, not laboratory-verified nutrition facts.
FOODS={
"breakfast":[
 {"name":"Oats with milk, banana and peanuts","diet":["vegetarian"],"kcal":430,"protein":18,"carbs":62,"fat":13,"tags":["oats","milk","banana","peanuts"]},
 {"name":"Eggs, whole-wheat toast and fruit","diet":["non-vegetarian"],"kcal":420,"protein":25,"carbs":43,"fat":15,"tags":["eggs","wheat","fruit"]},
 {"name":"Tofu bhurji with whole-wheat roti","diet":["vegetarian","vegan"],"kcal":390,"protein":24,"carbs":46,"fat":12,"tags":["tofu","wheat","soy"]},
 {"name":"Idli with sambar","diet":["vegetarian","vegan"],"kcal":360,"protein":13,"carbs":65,"fat":5,"tags":["rice","lentils"]}],
"lunch":[
 {"name":"Rice, dal, vegetables and curd","diet":["vegetarian"],"kcal":610,"protein":24,"carbs":91,"fat":15,"tags":["rice","lentils","dairy","curd"]},
 {"name":"Chicken, rice and vegetables","diet":["non-vegetarian"],"kcal":620,"protein":42,"carbs":72,"fat":14,"tags":["chicken","rice"]},
 {"name":"Rajma, rice and salad","diet":["vegetarian","vegan"],"kcal":590,"protein":22,"carbs":96,"fat":9,"tags":["beans","rice"]}],
"snack":[
 {"name":"Greek yogurt with fruit","diet":["vegetarian"],"kcal":220,"protein":17,"carbs":28,"fat":4,"tags":["yogurt","dairy"]},
 {"name":"Boiled eggs and fruit","diet":["non-vegetarian"],"kcal":230,"protein":13,"carbs":22,"fat":10,"tags":["eggs"]},
 {"name":"Roasted chana and fruit","diet":["vegetarian","vegan"],"kcal":240,"protein":11,"carbs":39,"fat":5,"tags":["chickpeas"]}],
"dinner":[
 {"name":"Paneer, roti and vegetables","diet":["vegetarian"],"kcal":560,"protein":31,"carbs":55,"fat":23,"tags":["paneer","wheat","dairy"]},
 {"name":"Fish, potatoes and vegetables","diet":["non-vegetarian"],"kcal":520,"protein":38,"carbs":48,"fat":16,"tags":["fish"]},
 {"name":"Chickpea curry, roti and vegetables","diet":["vegetarian","vegan"],"kcal":540,"protein":21,"carbs":82,"fat":13,"tags":["chickpeas","wheat"]}]}
def rnd(x): return int(round(x/5)*5)
def calculate_targets(p):
 age=int(p['age']); h=float(p['height_cm']); w=float(p['weight_kg']); sex=p.get('sex','unspecified')
 base=10*w+6.25*h-5*age
 bmr=base+(5 if sex=='male' else -161 if sex=='female' else -78)
 maintenance=bmr*ACTIVITY[p['activity_level']]; calories=rnd(max(1200,maintenance+ADJUST[p['goal']]))
 protein=rnd(w*PROTEIN[p['goal']]); fat=rnd(max(w*.7,calories*.25/9)); carbs=max(0,rnd((calories-protein*4-fat*9)/4))
 return {'bmr_kcal':rnd(bmr),'maintenance_kcal':rnd(maintenance),'daily_calories_kcal':calories,'protein_g':protein,'carbohydrates_g':carbs,'fat_g':fat,'method':'Mifflin-St Jeor estimate, activity multiplier and goal adjustment','disclaimer':'Nutrition values are estimates, not medical advice. Consult a qualified clinician or dietitian for medical conditions, pregnancy, eating-disorder history or medically prescribed diets.'}
# Ingredient-level nutrition estimates per reference portion; values are approximate.
_INGREDIENTS = {
 "oats": ("Rolled oats","g",60,233,10.14,39.78,4.14), "milk": ("Milk","ml",200,122,6.4,9.6,6.6),
 "banana": ("Banana","piece",1,105,1.3,27,0.4), "peanuts": ("Peanuts","g",10,57,2.58,1.61,4.92),
 "eggs": ("Eggs","piece",3,215,18.9,1.05,14.25), "bread": ("Whole-wheat bread","slice",2,148,7.8,24.6,2.52),
 "fruit": ("Seasonal fruit","piece",1,70,0.5,18,0.2), "tofu": ("Tofu","g",150,114,12,2.85,7.2),
 "roti": ("Whole-wheat roti","piece",2,238,7.76,44.56,3.36), "vegetables": ("Mixed vegetables","g",150,75,3.75,15,0.75),
 "idli": ("Idli","piece",3,174,6,36,1.2), "sambar": ("Sambar","ml",200,120,6,20,3),
 "rice": ("Cooked rice","g",220,286,5.94,62.04,0.66), "dal": ("Cooked dal","g",200,232,18,40,0.8),
 "curd": ("Curd","g",100,61,3.5,4.7,3.3), "chicken": ("Cooked chicken breast","g",150,248,46.5,0,5.4),
 "rajma": ("Cooked rajma","g",200,254,17.4,45.6,1), "yogurt": ("Greek yogurt","g",200,194,18,7.8,10),
 "chana": ("Roasted chana","g",50,190,11,29,3), "paneer": ("Paneer","g",120,318,21.96,1.44,24.96),
 "fish": ("Cooked fish","g",150,192,39,0,4.05), "potato": ("Boiled potato","g",250,218,4.75,50.25,0.25),
 "chickpeas": ("Cooked chickpeas","g",200,328,17.8,54.8,5.2)
}
_RECIPE_ALIASES = {
 "oats with milk banana and peanuts":["oats","milk","banana","peanuts"],
 "eggs whole wheat toast and fruit":["eggs","bread","fruit"],
 "tofu bhurji with whole wheat roti":["tofu","roti","vegetables"],
 "idli with sambar":["idli","sambar"], "rice dal vegetables and curd":["rice","dal","vegetables","curd"],
 "chicken rice and vegetables":["chicken","rice","vegetables"], "rajma rice and salad":["rajma","rice","vegetables"],
 "greek yogurt with fruit":["yogurt","fruit"], "boiled eggs and fruit":["eggs","fruit"],
 "roasted chana and fruit":["chana","fruit"], "paneer with roti and vegetables":["paneer","roti","vegetables"],
 "fish potatoes and vegetables":["fish","potato","vegetables"], "chickpea curry with roti and vegetables":["chickpeas","roti","vegetables"]
}
def _apply_ingredient_quantities(meals, target_kcal):
 prepared=[]
 # Keep countable foods in practical increments.
 count_steps={"eggs":1.0,"bread":1.0,"fruit":1.0,"banana":0.5,"roti":1.0,"idli":1.0}
 for meal in meals:
  normal=" ".join(re.findall(r"[a-z]+", str(meal.get("name","")).lower()))
  keys=_RECIPE_ALIASES.get(normal)
  if keys is None:
   for alias, recipe in _RECIPE_ALIASES.items():
    if len(set(alias.split()) & set(normal.split())) >= 3:
     keys=recipe
     break
  if keys is None:
   raise ValueError("No ingredient mapping for menu item: " + str(meal.get("name")))
  items=[]
  for key in keys:
   label,unit,qty,kcal,protein,carbs,fat=_INGREDIENTS[key]
   items.append({
    "name":label,"ingredient_key":key,"quantity":qty,"unit":unit,
    "reference_quantity":qty,"reference_unit":unit,
    "grams":qty if unit=="g" else (qty*118 if key=="banana" else qty*50 if key=="eggs" else qty*30 if key=="bread" else qty*40 if key=="roti" else qty*60 if key=="idli" else None),
    "millilitres":qty if unit=="ml" else None,
    "reference_kcal":kcal,"reference_protein":protein,
    "reference_carbs":carbs,"reference_fat":fat
   })
  prepared.append((meal,items))
 base=sum(sum(i["reference_kcal"] for i in items) for _,items in prepared)
 factor=max(0.5,min(float(target_kcal)/base if base else 1.0,2.5))
 result=[]
 for meal,items in prepared:
  for item in items:
   key=item["ingredient_key"]
   raw=item["reference_quantity"]*factor
   step=count_steps.get(key)
   quantity=round(raw/step)*step if step else raw
   quantity=max(step,quantity) if step else quantity
   ratio=quantity/item["reference_quantity"] if item["reference_quantity"] else 1.0
   item["quantity"]=round(quantity,2)
   if item["grams"] is not None:
    item["grams"]=round(item["grams"]*ratio,1)
   if item["millilitres"] is not None:
    item["millilitres"]=round(item["millilitres"]*ratio,1)
   for field,reference_field in (
    ("kcal","reference_kcal"),("protein","reference_protein"),
    ("carbs","reference_carbs"),("fat","reference_fat")
   ):
    item[field]=round(item[reference_field]*ratio,2)
   item["practical_portion"]=f'{item["quantity"]:g} {item["unit"]}'
   for field in ("reference_quantity","reference_unit","reference_kcal",
                 "reference_protein","reference_carbs","reference_fat","ingredient_key"):
    item.pop(field,None)
  for field in ("kcal","protein","carbs","fat"):
   meal[field]=int(round(sum(i[field] for i in items)))
  meal["ingredients"]=items
  meal["portion_multiplier"]=round(factor,2)
  meal["serving_note"]="Approximate portions; countable foods use practical increments. Nutrition is recalculated from the displayed portions."
  result.append(meal)
 return result
def select_meals(diet, allergies, target_kcal):
 allergies=[str(x).strip().lower() for x in allergies if str(x).strip()]
 aliases={"peanut":{"peanut","peanuts","groundnut","groundnuts","arachis"},"tree nut":{"almond","cashew","walnut","pistachio","hazelnut","pecan","macadamia","brazil nut"},"milk":{"milk","dairy","curd","yogurt","yoghurt","paneer","cheese","butter","ghee"},"dairy":{"milk","dairy","curd","yogurt","yoghurt","paneer","cheese","butter","ghee"},"soy":{"soy","soya","tofu"},"wheat":{"wheat","roti","bread","toast","flour","atta"},"gluten":{"wheat","roti","bread","toast","barley","rye","flour","atta"},"egg":{"egg","eggs"},"fish":{"fish"},"shellfish":{"shrimp","prawn","crab","lobster","shellfish"},"chickpea":{"chickpea","chickpeas","chana","gram"},"sesame":{"sesame","til","tahini"}}
 allergens=set()
 for a in allergies: allergens.update(aliases.get(a,{a}))
 result=[]
 for slot in ("breakfast","lunch","snack","dinner"):
  options=[]
  for food in FOODS[slot]:
   if diet not in food["diet"]: continue
   searchable=" ".join([food["name"],*food.get("tags",[])]).lower()
   words=set(re.findall(r"[a-z]+",searchable))
   if any(a in words or a in searchable for a in allergens): continue
   options.append(food)
  if not options: raise ValueError(f"No {slot} options remain after applying diet preference and allergies.")
  result.append({"meal":slot.title(),**options[0]})
 return _apply_ingredient_quantities(result, target_kcal)
def groq_explanation(p, targets, meals):
 key=os.getenv("GROQ_API_KEY"); model=os.getenv("GROQ_MODEL","openai/gpt-oss-120b")
 fallback="The targets and meals were generated by SmartFit rules. Configure GROQ_API_KEY to enable an optional explanation."
 if not key: return {"text":fallback,"status":"not_configured","model":None}
 prompt={"goal":p["goal"],"diet":p["dietary_preference"],"targets":targets,"meals":[{"meal":m["meal"],"name":m["name"],"kcal":m["kcal"],"protein_g":m["protein"]} for m in meals]}
 try:
  from groq import Groq
  client=Groq(api_key=key,timeout=15,max_retries=0)
  response=client.chat.completions.create(model=model,messages=[{"role":"system","content":"Explain this existing nutrition plan clearly and cautiously. Do not change numbers, add medical claims, or invent facts. Mention values and portions are estimates."},{"role":"user","content":json.dumps(prompt)}],max_tokens=220,temperature=0.2)
  content=response.choices[0].message.content
  if not content or not content.strip(): return {"text":"Plan generated; Groq returned an empty explanation. Nutrition targets and meals remain available.","status":"empty_response","model":model}
  return {"text":content.strip(),"status":"ok","model":model}
 except Exception as exc:
  return {"text":"Plan generated; optional Groq explanation unavailable. Nutrition targets and meals remain available.","status":"unavailable","model":model,"error_type":type(exc).__name__}
def build_diet_plan(p):
 targets=calculate_targets(p); meals=select_meals(p['dietary_preference'],p.get('allergies',[]),targets['daily_calories_kcal'])
 return {'profile':{'goal':p['goal'],'dietary_preference':p['dietary_preference'],'activity_level':p['activity_level']},'targets':targets,'meals':meals,'explanation':groq_explanation(p,targets,meals),'sources':[{'title':'Mifflin-St Jeor equation','publisher':'American Dietetic Association','url':'https://pubmed.ncbi.nlm.nih.gov/2305711/','scope':'Resting energy expenditure estimate.'}],'disclaimer':targets['disclaimer']}
