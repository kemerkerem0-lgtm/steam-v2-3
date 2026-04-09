from flask import Flask, render_template, request, jsonify
import requests
import random
import time

app = Flask(__name__)

# Steam API Yardımcı Fonksiyonu
def get_steam_data(endpoint, params={}):
    url = f"https://store.steampowered.com/api/{endpoint}"
    params.update({"cc": "tr", "l": "turkish", "t": int(time.time())})
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        return res.json()
    except:
        return None

@app.route("/")
def index():
    raw = get_steam_data("featuredcategories")
    content = {
        "featured": raw.get('featured_win', {}).get('items', [])[:3] if raw else [],
        "specials": raw.get('specials', {}).get('items', [])[:12] if raw else []
    }
    return render_template("index.html", content=content)

# 🔥 YAN BUTONLAR İÇİN ÖZEL FİLTRELER
@app.route("/api/filter/<type>")
def filter_games(type):
    raw = get_steam_data("featuredcategories")
    if not raw: return jsonify([])
    
    if type == "trend":
        return jsonify(raw.get('top_sellers', {}).get('items', []))
    elif type == "indirim":
        return jsonify(raw.get('specials', {}).get('items', []))
    elif type == "yeni":
        return jsonify(raw.get('new_releases', {}).get('items', []))
    elif type == "rastgele":
        # Tüm kategorilerden oyunları birleştir ve rastgele 1 tane seç
        all_games = raw.get('specials', {}).get('items', []) + raw.get('top_sellers', {}).get('items', [])
        return jsonify([random.choice(all_games)]) if all_games else jsonify([])
    return jsonify([])

# 🎮 DERİNLEMESİNE OYUN DETAYLARI
@app.route("/game/<int:app_id>")
def game_detail(app_id):
    # Oyun ana bilgileri
    data = get_steam_data("appdetails", {"appids": app_id})
    if data and data[str(app_id)]["success"]:
        game = data[str(app_id)]["data"]
        
        # Kullanıcı yorumlarını Steam'in ayrı API'sinden çekiyoruz
        rev_url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&l=turkish&num_per_page=5"
        reviews = requests.get(rev_url).json()
        
        return render_template("detail.html", game=game, reviews=reviews)
    return "Oyun verisi alınamadı.", 404

# 🔎 CANLI ARAMA
@app.route("/api/search")
def search():
    query = request.args.get("q", "")
    if len(query) < 2: return jsonify([])
    url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=turkish&cc=tr"
    res = requests.get(url).json()
    return jsonify(res.get("items", []))

if __name__ == "__main__":
    app.run(debug=True)