import urllib.request
import json

# Define the raw file URL for your JSON file
GITHUB_RAW_URL = "https://raw.githubusercontent.com/FuZionPanda1/DnDItemApp/main/items.json"

def fetch_items():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as url:
            data = url.read().decode()
            return json.loads(data)  # Parse JSON response
    except urllib.error.URLError as e:
        print(f"Failed to fetch data: {e.reason}")
        return []

def filter_items(items, rarity_choice, type_choice):
    if rarity_choice == "all" and type_choice == "all":
        return items
    if rarity_choice == "all":
        return [item for item in items if item['type'] == type_choice]
    if type_choice == "all":
        return [item for item in items if item['rarity'] == rarity_choice]
    return [item for item in items if item['rarity'] == rarity_choice and item['type'] == type_choice]

items = fetch_items()

rarity_options = ["all", "common", "uncommon", "rare", "legendary", "artifact"]
type_options = ["all", "weapon", "staff"]  # the magical item types

rarity_choice = input("What rarity of magic item are you looking for? : ").strip().lower()
type_choice = input("What type of magic item are you looking for? : ").strip().lower()

if rarity_choice in rarity_options and type_choice in type_options:
    filtered_items = filter_items(items, rarity_choice, type_choice)
    if filtered_items:
        item_names = [item['name'] for item in filtered_items]
        items_string = ", ".join(item_names)
        print(f"Here are the {rarity_choice} {type_choice} choices: {items_string}")
        check = input("Type the one you would like to read more about! ").strip().lower()
        
        # filtering
        found = False
        for item in filtered_items:
            if item['name'].lower() == check:
                print(f"Details about {item['name']}:")
                print(f"Name: {item['name']}")
                print(f"Rarity: {item['rarity']}")
                print(f"Type: {item['type']}")
                print(f"Description: {item['description']}")
                found = True
                break
                
        if not found:
            print(f"{check} not found in the list of {rarity_choice} {type_choice} items.")
    else:
        print(f"No items found for rarity: {rarity_choice} and type: {type_choice}")
else:
    print("Invalid rarity or type selection")
