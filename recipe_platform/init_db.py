"""
Initialisiert die Datenbank mit der neuen User-Struktur
"""
"""
Initialisiert die Datenbank mit der neuen User- und Rezept-Struktur
"""
import sqlite3
import json
import csv
from pathlib import Path

DATA_DIR = Path('data')
DB_PATH = DATA_DIR / 'recipes.db'
CSV_PATH = Path('..') / 'rezepte_100.csv'


def to_int(value, default=None):
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def load_csv_rows():
    if CSV_PATH.exists():
        with CSV_PATH.open('r', encoding='utf-8') as f:
            yield from csv.DictReader(f)
    else:
        print("CSV-Datei nicht gefunden, erstelle Beispielrezepte...")
        beispiele = [
            {
                'titel': 'Spaghetti Carbonara',
                'beschreibung': 'Klassisches italienisches Pasta-Gericht',
                'kategorie': 'Hauptgericht',
                'kuche': 'Italienisch',
                'portionen': 4,
                'gesamtzeit_min': 25,
                'zutaten': ['400g Spaghetti', '200g Speck', '4 Eier', '100g Parmesan', 'Salz', 'Pfeffer'],
                'schritte': ['Pasta kochen', 'Speck anbraten', 'Eier mit Käse mischen', 'Alles vermengen']
            },
            {
                'titel': 'Caesar Salad',
                'beschreibung': 'Frischer Salat mit Hähnchen',
                'kategorie': 'Salat',
                'kuche': 'Amerikanisch',
                'portionen': 2,
                'gesamtzeit_min': 20,
                'zutaten': ['Römersalat', 'Hähnchenbrust', 'Croutons', 'Parmesan', 'Caesar Dressing'],
                'schritte': ['Salat waschen', 'Hähnchen braten', 'Alles mischen', 'Mit Dressing servieren']
            },
            {
                'titel': 'Tomatensuppe',
                'beschreibung': 'Cremige Tomatensuppe',
                'kategorie': 'Suppe',
                'kuche': 'International',
                'portionen': 4,
                'gesamtzeit_min': 30,
                'zutaten': ['1kg Tomaten', '1 Zwiebel', '2 Knoblauchzehen', 'Sahne', 'Basilikum'],
                'schritte': ['Zwiebeln anschwitzen', 'Tomaten hinzufügen', 'Köcheln lassen', 'Pürieren']
            }
        ]
        for eintrag in beispiele:
            yield {
                'titel': eintrag['titel'],
                'beschreibung': eintrag['beschreibung'],
                'kategorie': eintrag['kategorie'],
                'kuche': eintrag['kuche'],
                'ernahrung': '',
                'portionen': eintrag['portionen'],
                'gesamtzeit_min': eintrag['gesamtzeit_min'],
                'zutaten_json': json.dumps(eintrag['zutaten'], ensure_ascii=False),
                'schritte_json': json.dumps(eintrag['schritte'], ensure_ascii=False),
                'autor': 'Team FreshCook'
            }


def parse_list_field(row, json_key, fallback_key=None, delimiter=','):
    raw = row.get(json_key)
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    if fallback_key and row.get(fallback_key):
        sep = delimiter
        if delimiter == '.':
            sep = '.'
        return [item.strip() for item in row[fallback_key].split(sep) if item.strip()]
    return []


def init_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lösche alte Tabellen
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS ratings')
    cursor.execute('DROP TABLE IF EXISTS favorites')
    cursor.execute('DROP TABLE IF EXISTS recipes')
    
    # Erstelle Users-Tabelle
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            consent_marketing BOOLEAN DEFAULT 0,
            consent_analytics BOOLEAN DEFAULT 0,
            data_processing_consent BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_login TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            deletion_requested_at TIMESTAMP,
            export_requested_at TIMESTAMP
        )
    ''')
    
    # Erstelle Recipes-Tabelle mit voller ORM-Struktur
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titel TEXT NOT NULL,
            beschreibung TEXT,
            kategorie TEXT,
            zielgruppe TEXT,
            kuche TEXT,
            ernahrung TEXT,
            schwierigkeitsgrad TEXT,
            portionen INTEGER,
            vorbereitungszeit_min INTEGER,
            kochzeit_min INTEGER,
            gesamtzeit_min INTEGER,
            kalorien_kcal INTEGER,
            protein_g INTEGER,
            kohlenhydrate_g INTEGER,
            fett_g INTEGER,
            allergene TEXT,
            tags TEXT,
            bewertung REAL,
            avg_rating REAL DEFAULT 0,
            ratings_count INTEGER DEFAULT 0,
            autor TEXT,
            zutaten_json TEXT,
            schritte_json TEXT,
            sprache TEXT DEFAULT 'de',
            seo_slug TEXT UNIQUE,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Erstelle Ratings-Tabelle
    cursor.execute('''
        CREATE TABLE ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            stars INTEGER NOT NULL CHECK(stars >= 1 AND stars <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            UNIQUE(user_id, recipe_id)
        )
    ''')
    
    # Erstelle Favorites-Tabelle
    cursor.execute('''
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            UNIQUE(user_id, recipe_id)
        )
    ''')
    
    insert_sql = '''
        INSERT INTO recipes (
            titel, beschreibung, kategorie, zielgruppe, kuche, ernahrung,
            schwierigkeitsgrad, portionen, vorbereitungszeit_min, kochzeit_min,
            gesamtzeit_min, kalorien_kcal, protein_g, kohlenhydrate_g, fett_g,
            allergene, tags, bewertung, avg_rating, ratings_count, autor,
            zutaten_json, schritte_json, sprache, seo_slug
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    for row in load_csv_rows():
        zutaten = parse_list_field(row, 'zutaten_json', 'zutaten', ',')
        schritte = parse_list_field(row, 'schritte_json', 'schritte', '.')
        
        cursor.execute(insert_sql, (
            row.get('titel', 'Unbekannt'),
            row.get('beschreibung', ''),
            row.get('kategorie', ''),
            row.get('zielgruppe', ''),
            row.get('kuche', ''),
            row.get('ernahrung', ''),
            row.get('schwierigkeitsgrad', ''),
            to_int(row.get('portionen'), 4),
            to_int(row.get('vorbereitungszeit_min')),
            to_int(row.get('kochzeit_min')),
            to_int(row.get('gesamtzeit_min'), 30),
            to_int(row.get('kalorien_kcal')),
            to_int(row.get('protein_g')),
            to_int(row.get('kohlenhydrate_g')),
            to_int(row.get('fett_g')),
            row.get('allergene', ''),
            row.get('tags', ''),
            float(row['bewertung']) if row.get('bewertung') else None,
            float(row['avg_rating']) if row.get('avg_rating') else 0,
            to_int(row.get('ratings_count'), 0),
            row.get('autor', 'Team FreshCook'),
            json.dumps(zutaten, ensure_ascii=False),
            json.dumps(schritte, ensure_ascii=False),
            row.get('sprache', 'de'),
            row.get('seo_slug')
        ))
    
    conn.commit()
    
    # Zeige Statistiken
    cursor.execute('SELECT COUNT(*) FROM recipes')
    recipe_count = cursor.fetchone()[0]
    
    print(f"[OK] Datenbank erfolgreich initialisiert!")
    print(f"[INFO] {recipe_count} Rezepte geladen")
    
    conn.close()


if __name__ == '__main__':
    init_database()
