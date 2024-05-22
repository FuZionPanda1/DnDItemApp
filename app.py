from flask import Flask, request, render_template
import urllib.request
import json

app = Flask(__name__)

GITHUB_RAW_URL = "https://raw.githubusercontent.com/FuZionPanda1/DnDItemApp/main/items.json"

def fetch_items():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as url:
            data = url.read().decode()
            return json.loads(data)
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
type_options = ["all", "weapon", "staff", "wondrous item"]


@app.route('/')
def index():
    return render_template('index.html', rarity_options=rarity_options, type_options=type_options)

@app.route('/filter', methods=['POST'])
def filter():
    rarity_choice = request.form.get('rarity_choice').strip().lower()
    type_choice = request.form.get('type_choice').strip().lower()

    if rarity_choice in rarity_options and type_choice in type_options:
        filtered_items = filter_items(items, rarity_choice, type_choice)
        return render_template('results.html', items=filtered_items, rarity_choice=rarity_choice, type_choice=type_choice)
    else:
        return "Invalid rarity or type selection", 400

@app.route('/item/<item_name>')
def item_details(item_name):
    item_name = item_name.lower()
    selected_item = next((item for item in items if item['name'].lower() == item_name), None)
    if selected_item:
        return render_template('item.html', item=selected_item)
    else:
        return render_template('error.html', message=f"Item '{item_name}' not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
