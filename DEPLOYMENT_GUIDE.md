# 🚀 FreshCook auf GitHub veröffentlichen

## ✅ Status
- Git Repository: Initialisiert
- Dateien committed: 60 Files
- Bereit für GitHub Push

---

## 📋 Schritt 1: GitHub Repository erstellen

1. Öffne: **https://github.com/new**
2. Fülle aus:
   - **Repository name**: `freshcook-recipe-platform`
   - **Description**: `Moderne Rezeptplattform mit FastAPI Backend und Vanilla JavaScript Frontend`
   - **Visibility**: **Public**
3. **WICHTIG**: Nichts anhaken (kein README, kein .gitignore, keine License)
4. Klick: **Create repository**

---

## 📋 Schritt 2: Repository URL kopieren

GitHub zeigt dir jetzt eine Seite mit Befehlen. Kopiere die URL:
```
https://github.com/DEIN-USERNAME/freshcook-recipe-platform.git
```

---

## 📋 Schritt 3: Terminal-Befehle ausführen

```bash
cd "c:\Users\mikew\Agiles Projektmanagement"

git remote add origin https://github.com/DEIN-USERNAME/freshcook-recipe-platform.git

git branch -M main

git push -u origin main
```

**WICHTIG**: Ersetze `DEIN-USERNAME` mit deinem GitHub Username!

---

## 🌐 Als Website veröffentlichen

### Option A: Render.com (EMPFOHLEN - Vollständige App)

1. Gehe zu: **https://render.com**
2. Registriere dich mit GitHub Account
3. Klick **New +** → **Web Service**
4. Verbinde dein Repository
5. Einstellungen:
   - **Name**: `freshcook-platform`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r recipe_platform/requirements.txt`
   - **Start Command**: `cd recipe_platform && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Klick **Create Web Service**

Nach 5-10 Minuten ist deine App online unter:
```
https://freshcook-platform.onrender.com
```

### Option B: GitHub Pages (Nur Frontend)

1. Repository → **Settings** → **Pages**
2. **Source**: main branch
3. **Save**

Nach 2 Minuten online unter:
```
https://DEIN-USERNAME.github.io/freshcook-recipe-platform/
```

**HINWEIS**: Backend läuft nicht auf GitHub Pages!

---

## 👥 Kollegen einladen

Teile die URL:
- **Render**: `https://freshcook-platform.onrender.com`
- **GitHub**: `https://github.com/DEIN-USERNAME/freshcook-recipe-platform`

---

## 📝 Lokale Installation für Kollegen

```bash
git clone https://github.com/DEIN-USERNAME/freshcook-recipe-platform.git
cd freshcook-recipe-platform/recipe_platform
# Doppelklick auf start.bat
```
