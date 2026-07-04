# ============================================================
# app.py — Blood Donor Finder
# This is the MAIN file. Run this file to start the website.
#
# What this file does:
#   - Creates the Flask web app
#   - Defines URL routes (pages of the website)
#   - Connects user requests to database functions
#
# Pages in this project:
#   /           → Home page + Search donors
#   /register   → Form to become a donor
#   /admin      → Admin dashboard (see all donors)
#
# How Flask works (simple explanation):
#   User visits a URL → Flask finds the matching function
#   → Function runs → HTML page is sent back to user
# ============================================================

# Import Flask and the tools we need
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Import all our database functions from model.py
from model import (
    setup_database,
    save_new_donor,
    find_donors,
    get_all_donors,
    flip_donor_availability,
    get_dashboard_stats,
    check_donor_data,
    all_blood_groups
)

# Create the Flask app
# __name__ tells Flask where to look for templates and static files
app = Flask(__name__)

# Secret key is needed for flash messages (success/error popups)
app.secret_key = '+secret_key'


# ============================================================
# APP STARTUP
# This runs ONCE when the app first starts.
# It creates the database and table if they don't exist.
# ============================================================
db_ready = False

@app.before_request
def prepare_database():
    global db_ready
    if not db_ready:
        setup_database()
        db_ready = True


# ============================================================
# PAGE 1: HOME PAGE  (URL: /)
# Shows the search form.
# If the user fills the form and clicks Search,
# this same page shows the results below.
# ============================================================
@app.route('/')
def home_page():
    # Get search values from the URL
    # Example URL: /?group=A+&city=Chennai
    search_group = request.args.get('group', '').strip().upper()
    search_city  = request.args.get('city', '').strip()

    # Start with empty results
    donor_results = []
    search_done   = False
    error_message = None

    # If the user typed both group and city, do the search
    if search_group and search_city:
        search_done = True

        # Make sure the blood group they typed is valid
        if search_group not in all_blood_groups:
            error_message = 'Please select a valid blood group.'
        else:
            # Search the database and get matching donors
            donor_results = find_donors(search_group, search_city)

    # Send all data to the HTML template to display
    return render_template(
        'index.html',
        blood_groups   = all_blood_groups,
        donors         = donor_results,
        search_done    = search_done,
        search_group   = search_group,
        search_city    = search_city,
        error_message  = error_message
    )


# ============================================================
# PAGE 2: REGISTER PAGE  (URL: /register)
#
# GET request  → Just show the empty registration form
# POST request → User submitted the form, save to database
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register_page():

    # ── POST: User submitted the form ──
    if request.method == 'POST':

        # Collect all form values
        form_data = {
            'name':        request.form.get('name', ''),
            'blood_group': request.form.get('blood_group', ''),
            'city':        request.form.get('city', ''),
            'phone':       request.form.get('phone', '')
        }
        

        # Check if the data is valid
        is_valid, error_message = check_donor_data(form_data)

        if not is_valid:
            # Show the error and keep the form filled
            flash(error_message, 'error')
            return render_template('register.html', blood_groups=all_blood_groups, form={})

        # Data is valid — save to database
        save_new_donor(
            name        = form_data['name'],
            blood_group = form_data['blood_group'],
            city        = form_data['city'],
            phone       = form_data['phone']
        )

        # Show success message and go to home page
        flash('Thank you! You are now registered as a blood donor. 🩸', 'success')
        return redirect(url_for('home_page'))

    # ── GET: Just show the empty form ──
    return render_template('register.html', blood_groups=all_blood_groups, form={})


# ============================================================
# PAGE 3: ADMIN DASHBOARD  (URL: /admin)
# Shows all donors and statistics.
# ============================================================
@app.route('/admin')
def admin_page():
    all_donors = get_all_donors()
    stats      = get_dashboard_stats()

    return render_template(
        'admin.html',
        donors       = all_donors,
        stats        = stats,
        blood_groups = all_blood_groups,
        
    )


# ============================================================
# ACTION: TOGGLE AVAILABILITY  (URL: /admin/toggle/ID)
# This is called by JavaScript when admin clicks a button.
# It flips the donor's status between Available/Unavailable.
# Returns JSON (not a full HTML page).
# ============================================================
@app.route('/admin/toggle/<int:donor_id>', methods=['POST'])
def toggle_donor(donor_id):
    new_value = flip_donor_availability(donor_id)

    if new_value is None:
        # Donor not found
        return jsonify({'status': 'error', 'message': 'Donor not found'}), 404

    # Send back the result as JSON
    return jsonify({'status': 'ok', 'available': new_value})


# ============================================================
# API ROUTE: JSON SEARCH  (URL: /api/search?group=A+&city=Chennai)
# This returns donor data as JSON instead of HTML.
# Useful if someone wants to use the data in another app.
# ============================================================
@app.route('/api/search')
def api_search():
    search_group = request.args.get('group', '').strip().upper()
    search_city  = request.args.get('city', '').strip()

    # Both fields are required
    if not search_group or not search_city:
        return jsonify({'error': 'Please provide both group and city'}), 400

    if search_group not in all_blood_groups:
        return jsonify({'error': 'Invalid blood group'}), 400

    donors = find_donors(search_group, search_city)
    return jsonify(donors)


# ============================================================
# START THE APP
# debug=True means: show detailed errors during development
# Change to debug=False when you go live (production)
# ============================================================
if __name__ == '__main__':
    app.run(debug=True)