from flask import Flask, request, render_template, redirect, url_for, flash
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


GITHUB_RAW_URL = "https://raw.githubusercontent.com/FuZionPanda1/DnDItemApp/main/items.json"

GITHUB_HOMEBREW_URL = "https://raw.githubusercontent.com/FuZionPanda1/DnDItemApp/main/homebrew_items.json"

RARITY_ORDER = {
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "very rare": 4,
    "legendary": 5,
    "artifact": 6
}

PLACEHOLDER_IMAGES = {
    "common": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/common_placeholder.png?raw=true",
    "uncommon": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/placeholder_uncommon.png?raw=true",
    "rare": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/placeholder_rare.png?raw=true",
    "very rare": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/placeholder_veryrare.png?raw=true",
    "legendary": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/placeholder_legendary.png?raw=true",
    "artifact": "https://github.com/FuZionPanda1/DnDItemApp/blob/main/images/placeholder_artifact.png?raw=true"
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def fetch_items():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as url:
            data = url.read().decode()
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"Failed to fetch data: {e.reason}")
        return []
    
def fetch_homebrew_items():
    try:
        with urllib.request.urlopen(GITHUB_HOMEBREW_URL) as url:
            data = url.read().decode()
            return json.loads(data)
    except urllib.error.URLError as e:
        print(f"Failed to fetch homebrew data: {e.reason}")
        return []    

def filter_items(items, rarity_choice, type_choice, source_choice):
    filtered = items
    if rarity_choice != "all":
        filtered = [item for item in filtered if item['rarity'] == rarity_choice]
    if type_choice != "all":
        filtered = [item for item in filtered if item['type'] == type_choice]
    if source_choice != "ALL":
        filtered = [item for item in filtered if item['source'] == source_choice]
    return sorted(filtered, key=lambda item: RARITY_ORDER.get(item['rarity'], float('inf')))

def filter_homebrew_items(items, rarity_choice, type_choice):
    hb_filtered = items
    if rarity_choice != "":
        if rarity_choice != "all":
            hb_filtered = [item for item in hb_filtered if item['rarity'] == rarity_choice]
        if type_choice != "all":
            hb_filtered = [item for item in hb_filtered if item['type'] == type_choice]
    return sorted(hb_filtered, key=lambda item: RARITY_ORDER.get(item['rarity'], float('inf')))





items = fetch_items()
homebrew_items = fetch_homebrew_items()

rarity_options = ["all", "common", "uncommon", "rare", "very rare", "legendary", "artifact"]
type_options = ["all", "armor", "weapon", "staff", "ring", "wondrous item", "wand"]
source_options = ["all", "SRD", "TCE", "XGE"]
race_options = ["human", "not human","custom"]
class_options = ["enployed","unenployed","custom"]

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create-character')
def create_character():
    return render_template('character_form.html', race_options = race_options, class_options = class_options)

@app.route('/upload-character')
def upload_character_form():
    return render_template('upload_form.html')

@app.route('/upload-character', methods=['POST'])
def upload_character():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and file.filename.endswith('.dnp'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('display_character', filename=file.filename))
    else:
        flash('Invalid file type')
        return redirect(request.url)

@app.route('/character/<filename>')
def display_character(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'r') as file:
        character = json.load(file)
    return render_template('character_sheet.html', character=character)

@app.route('/filters')
def filters():
    return render_template('filters.html')

@app.route('/official/filter')
def official_index():
    return render_template('official_index.html', rarity_options=rarity_options, type_options=type_options, source_options=source_options)

@app.route('/homebrew/filter')
def homebrew_index():
    return render_template('homebrew_index.html', rarity_options=rarity_options, type_options=type_options)

@app.route('/official/result', methods=['POST'])
def official_filter():
    rarity_choice = request.form.get('rarity_choice').strip().lower()
    type_choice = request.form.get('type_choice').strip().lower()
    source_choice = request.form.get('source_choice').strip().upper()

    if rarity_choice in [option.lower() for option in rarity_options] and type_choice in [option.lower() for option in type_options] and source_choice in [option.upper() for option in source_options]:
        filtered_items = filter_items(items, rarity_choice, type_choice, source_choice)
        return render_template('official_results.html', items=filtered_items, rarity_choice=rarity_choice, type_choice=type_choice, source_choice=source_choice)
    else:
        return "Invalid rarity, type, or source selection", 400
    
@app.route('/homebrew/result', methods=['POST'])
def homebrew_filter():
    rarity_choice = request.form.get('rarity_choice').strip().lower()
    type_choice = request.form.get('type_choice').strip().lower()

    if rarity_choice in [option.lower() for option in rarity_options] and type_choice in [option.lower() for option in type_options]:
        hb_filtered_items = filter_homebrew_items(homebrew_items, rarity_choice, type_choice)
        return render_template('homebrew_results.html', items=hb_filtered_items, rarity_choice=rarity_choice, type_choice=type_choice, source_choice="n/a")
    else:
        return "Invalid rarity or type selection", 400

@app.route('/item/<item_name>')
def item_details(item_name):
    item_name = item_name.lower()
    selected_item = next((item for item in items if item['name'].lower() == item_name), None)
    if selected_item:
        rarity = selected_item['rarity']
        placeholder_image = PLACEHOLDER_IMAGES.get(rarity, PLACEHOLDER_IMAGES['common'])
        return render_template('item.html', item=selected_item, placeholder_image=placeholder_image)
    else:
        return render_template('error.html', message=f"Item '{item_name}' not found"), 404
    
@app.route('/homebrew/item/<item_name>')
def homebrew_item_details(item_name):
    item_name = item_name.lower()
    selected_item = next((item for item in homebrew_items if item['name'].lower() == item_name), None)
    if selected_item:
        rarity = selected_item['rarity']
        placeholder_image = PLACEHOLDER_IMAGES.get(rarity, PLACEHOLDER_IMAGES['common'])
        return render_template('item.html', item=selected_item, placeholder_image=placeholder_image)
    else:
        return render_template('error.html', message=f"Item '{item_name}' not found"), 404
    

if __name__ == '__main__':
    app.run(debug=True)
