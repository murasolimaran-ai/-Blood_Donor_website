# 🩸 BloodConnect — Blood Donor Finder
### A Student Project | Built with Python, Flask, MySQL

---

## 📁 Folder Structure

```
blood_donor_finder/
│
├── app.py              ← MAIN FILE — Start the website by running this
├── model.py            ← DATABASE FILE — All database logic lives here
├── requirements.txt    ← Python libraries needed
├── README.md           ← This file (project explanation)
│
├── templates/          ← HTML pages (what the user sees)
│   ├── index.html      ← Home page + Search results
│   ├── register.html   ← Donor registration form
│   └── admin.html      ← Admin dashboard
│
└── static/             ← CSS and JavaScript files
    ├── css/
    │   └── style.css   ← All page styling
    └── js/
        └── ui.js       ← Small UI effects only
```

---

## 🧠 How The Project Works (Simple Explanation)

```
User visits website
       ↓
app.py receives the request
       ↓
app.py calls a function in model.py
       ↓
model.py runs SQL query on MySQL database
       ↓
model.py returns data to app.py
       ↓
app.py sends data to HTML template
       ↓
HTML page is shown to the user
```

---

## 📄 File Explanations

### app.py (Controller)
- This is the MAIN file. Run it to start the website.
- It defines URL routes (like `/`, `/register`, `/admin`)
- Each route is a Python function
- It does NOT contain database logic — that's in model.py

### model.py (Model / Database Layer)
- Connects to MySQL
- Creates database and table on startup
- Has functions for: save donor, search donors, get all donors, toggle availability, get stats
- All SQL queries are here

### templates/ (View Layer)
- HTML files that Flask fills with data
- Uses Jinja2 `{{ variable }}` syntax to show Python data in HTML
- `{% for %}` loops work like Python for loops

### static/ (Frontend Files)
- CSS: Makes the website look good
- JS: Only small UI effects (toast, loading, auto-hide messages)

---

## 🚀 How To Run This Project

### Step 1: Install Python libraries
```bash
pip install -r requirements.txt
```

### Step 2: Make sure MySQL is running
Start MySQL on your computer.

### Step 3: Set your database password (if needed)
Open `model.py` and change:
```python
DB_PASSWORD = ''    # ← Put your MySQL password here
```

### Step 4: Run the app
```bash
python app.py
```

### Step 5: Open in browser
Go to: `http://localhost:5000`

---

## 📊 Database Table Structure

```sql
CREATE TABLE donors (
    id          INT AUTO_INCREMENT PRIMARY KEY,  -- Auto number
    name        VARCHAR(100),                    -- Full name
    blood_group VARCHAR(5),                      -- Like A+, B-, O+
    city        VARCHAR(100),                    -- City name (lowercase)
    phone       VARCHAR(20),                     -- Phone number
    available   INT DEFAULT 1,                   -- 1=available, 0=not
    joined_on   DATETIME DEFAULT NOW()           -- Registration time
)
```

---

## 🩸 Blood Group Compatibility Table

| Patient Needs | Can Accept From |
|---|---|
| A+  | A+, A-, O+, O- |
| A-  | A-, O- |
| B+  | B+, B-, O+, O- |
| B-  | B-, O- |
| AB+ | A+, A-, B+, B-, O+, O-, AB+, AB- |
| AB- | A-, B-, O-, AB- |
| O+  | O+, O- |
| O-  | O- |

---

## 🐛 The Bug That Was Fixed

**Problem:** If a donor registered with blood group `o+` (lowercase),
the search query `WHERE blood_group = 'O+'` would NOT find them.

**Fix:** In `model.py`, inside `save_new_donor()` function:
```python
blood_group.upper()   # Converts 'o+' → 'O+' before saving
city.lower()          # Converts 'Chennai' → 'chennai' before saving
```
This ensures all data is stored in the same format so search always works.

---

## 🎓 Viva Questions & Answers

**Q: What is Flask?**
A: Flask is a Python library that helps us create websites. It handles URL routing and HTML rendering.

**Q: What is MVC architecture?**
A: Model-View-Controller.
- Model = model.py (database)
- View = templates/ (HTML pages)
- Controller = app.py (routes)

**Q: Why is model.py separate from app.py?**
A: To keep the code organized. Database logic and website logic are different things. Separating them makes the code easier to read and fix.

**Q: What is Jinja2?**
A: It's the template language Flask uses. It lets us put Python variables inside HTML using `{{ variable }}` syntax.

**Q: Why do we use `.upper()` on blood group?**
A: To fix a bug. MySQL is case-sensitive in comparisons. If we store `o+` but search for `O+`, it won't match. By always storing in uppercase, search always works.

**Q: What does `available = 1` mean in the database?**
A: 1 means the donor is currently available. 0 means unavailable. This is called a boolean stored as an integer.