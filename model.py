# ============================================================
# model.py — Blood Donor Finder
# This file handles ALL database work.
# Think of this as the "brain" of the project.
#
# What this file does:
#   1. Connects to MySQL database
#   2. Creates the donors table
#   3. Saves new donors
#   4. Searches for matching donors
#   5. Shows all donors (for admin)
#   6. Turns a donor ON or OFF
#   7. Counts how many donors exist
# ============================================================

# We need this library to talk to MySQL
import mysql.connector


# ============================================================
# BLOOD GROUP COMPATIBILITY TABLE
# This tells us: "If someone needs blood group X,
# which donor blood groups can they accept?"
#
# Example: If patient needs A+,
#          donors with A+, A-, O+, or O- can help.
# ============================================================
compatible_donors = {
    'A+':  ['A+', 'A-', 'O+', 'O-'],
    'A-':  ['A-', 'O-'],
    'B+':  ['B+', 'B-', 'O+', 'O-'],
    'B-':  ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
    'AB-': ['A-', 'B-', 'O-', 'AB-'],
    'O+':  ['O+', 'O-'],
    'O-':  ['O-'],
}

# Simple list of all valid blood groups
all_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


# ============================================================
# DATABASE SETTINGS
# Change these values to match YOUR MySQL setup
# ============================================================
DB_HOST     = 'localhost'   # Where MySQL is running
DB_USER     = 'root'        # Your MySQL username
DB_PASSWORD = 'user_name'            # Your MySQL password
DB_NAME     = 'DB_name'  # The database name we will create


# ============================================================
# FUNCTION: connect_to_database()
# Opens a connection to MySQL and returns it.
# We call this every time we need to talk to the database.
# ============================================================
def connect_to_database():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection


# ============================================================
# FUNCTION: setup_database()
# Creates the database and the donors table.
# This runs once when the app starts.
#
# The donors table has these columns:
#   id          - Auto number (1, 2, 3, ...)
#   name        - Donor's full name
#   blood_group - Like A+, B-, O+, etc.
#   city        - City where donor lives
#   phone       - Contact number
#   available   - 1 = ready to donate, 0 = not available
#   registered_at   - Date and time they registered
# ============================================================
def setup_database():
    # Step 1: Connect WITHOUT choosing a database first
    #         because we need to CREATE it first
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()

    # Step 2: Create the database if it doesn't already exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS blood_donor_db")
    cursor.execute("USE blood_donor_db")

    # Step 3: Create the donors table
    #         IF NOT EXISTS means: don't crash if it already exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(100) NOT NULL,
            blood_group VARCHAR(5)   NOT NULL,
            city        VARCHAR(100) NOT NULL,
            phone       VARCHAR(20)  NOT NULL,
            available   TINYINT(1)   NOT NULL DEFAULT 1,
            registered_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Save changes and close
    connection.commit()
    cursor.close()
    connection.close()


# ============================================================
# FUNCTION: check_donor_data(data)
# Checks if the form data is valid before saving to database.
# Returns two things: (True/False, error message)
#
# Example:
#   is_ok, message = check_donor_data(form_data)
#   if is_ok:
#       save to database
#   else:
#       show the error message
# ============================================================
def check_donor_data(data):
    # Get each field and remove extra spaces
    name        = data.get('name', '').strip()
    blood_group = data.get('blood_group', '').strip().upper()
    city        = data.get('city', '').strip()
    phone       = data.get('phone', '').strip()

    # Check: name must be at least 2 characters
    if len(name) < 2:
        return False, 'Name must be at least 2 characters long.'

    # Check: blood group must be a valid one
    if blood_group not in all_blood_groups:
        return False, 'Please select a valid blood group from the list.'

    # Check: city must be at least 2 characters
    if len(city) < 2:
        return False, 'City name must be at least 2 characters long.'

    # Check: phone must be at least 7 digits
    if len(phone) < 7:
        return False, 'Phone number must be at least 7 digits long.'

    # All checks passed!
    return True, ''


# ============================================================
# FUNCTION: save_new_donor(name, blood_group, city, phone)
# Saves a new donor into the database.
# Returns the ID number of the new donor.
#
# IMPORTANT: We always store blood_group in UPPERCASE
# and city in lowercase so search always works correctly.
# (This fixes the bug where 'o+' didn't match 'O+')
# ============================================================
def save_new_donor(name, blood_group, city, phone):
    connection = connect_to_database()
    cursor = connection.cursor()

    # SQL INSERT command to add a new row
    sql = "INSERT INTO donors (name, blood_group, city, phone) VALUES (%s, %s, %s, %s)"

    # We use .upper() on blood_group so 'o+' becomes 'O+'
    # We use .lower() on city so 'Chennai' and 'chennai' both work
    values = (
        name.strip(),
        blood_group.upper(),   # Fix: always store as uppercase
        city.strip().lower(),  # Fix: always store as lowercase
        phone.strip()
    )

    cursor.execute(sql, values)
    connection.commit()

    # lastrowid gives us the ID of the row we just inserted
    new_donor_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return new_donor_id


# ============================================================
# FUNCTION: find_donors(blood_group, city)
# Searches for available donors who match:
#   1. A compatible blood group for the patient
#   2. The same city
#
# Returns a list of donors (each donor is a dictionary)
# ============================================================
def find_donors(blood_group, city):
    # Convert to standard format
    blood_group = blood_group.upper()
    city = city.strip().lower()

    # Get the list of compatible donor blood groups
    # Example: patient needs A+ → search for ['A+', 'A-', 'O+', 'O-']
    matching_groups = compatible_donors.get(blood_group, [blood_group])

    # Build placeholders for the SQL query
    # If we have 4 groups, we need: %s, %s, %s, %s
    placeholders = ', '.join(['%s'] * len(matching_groups))

    connection = connect_to_database()
    cursor = connection.cursor()

    # Search for donors who:
    #   - Have a compatible blood group (IN list)
    #   - Live in the same city
    #   - Are currently available (available = 1)
    sql = f"""
        SELECT id, name, blood_group, city, phone, available, registered_at
        FROM donors
        WHERE blood_group IN ({placeholders})
          AND city = %s
          AND available = 1
        ORDER BY registered_at DESC
    """

    # Combine the groups list + city into one tuple for the query
    cursor.execute(sql, matching_groups + [city])
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # Convert each row (tuple) into a simple dictionary
    # This makes it easy to use in HTML templates
    donor_list = []
    for row in rows:
        donor = {
            'id':          row[0],
            'name':        row[1],
            'blood_group': row[2],
            'city':        row[3].title(),   # "chennai" → "Chennai"
            'phone':       row[4],
            'available':   row[5],
            'registered_at':   str(row[6])
        }
        donor_list.append(donor)

    return donor_list


# ============================================================
# FUNCTION: get_all_donors()
# Returns ALL donors from the database.
# Used by the admin page to show the full list.
# ============================================================
def get_all_donors():
    connection = connect_to_database()
    cursor = connection.cursor()

    sql = """
        SELECT id, name, blood_group, city, phone, available, registered_at
        FROM donors
        ORDER BY registered_at DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # Convert each row into a dictionary
    donor_list = []
    for row in rows:
        donor = {
            'id':          row[0],
            'name':        row[1],
            'blood_group': row[2],
            'city':        row[3].title(),
            'phone':       row[4],
            'available':   row[5],
            'registered_at':   str(row[6])
        }
        donor_list.append(donor)

    return donor_list


# ============================================================
# FUNCTION: flip_donor_availability(donor_id)
# Switches a donor between Available and Unavailable.
# If available = 1, change to 0. If 0, change to 1.
# Returns the NEW value (1 or 0).
# ============================================================
def flip_donor_availability(donor_id):
    connection = connect_to_database()
    cursor = connection.cursor()

    # Step 1: Find the current availability of this donor
    cursor.execute("SELECT available FROM donors WHERE id = %s", (donor_id,))
    row = cursor.fetchone()

    # If donor not found, return an error
    if row is None:
        cursor.close()
        connection.close()
        return None

    current_value = row[0]

    # Step 2: Flip the value (1 → 0, or 0 → 1)
    if current_value == 1:
        new_value = 0
    else:
        new_value = 1

    # Step 3: Save the new value to database
    cursor.execute(
        "UPDATE donors SET available = %s WHERE id = %s",
        (new_value, donor_id)
    )
    connection.commit()

    cursor.close()
    connection.close()

    return new_value


# ============================================================
# FUNCTION: get_dashboard_stats()
# Collects numbers for the admin dashboard:
#   - Total donors
#   - How many are available
#   - How many per blood group
#   - Top 5 cities
# ============================================================
def get_dashboard_stats():
    connection = connect_to_database()
    cursor = connection.cursor()

    # Count total donors
    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donors = cursor.fetchone()[0]

    # Count donors who are available right now
    cursor.execute("SELECT COUNT(*) FROM donors WHERE available = 1")
    available_donors = cursor.fetchone()[0]

    # Count donors per blood group
    cursor.execute("SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group")
    group_rows = cursor.fetchall()
    count_by_group = {}
    for row in group_rows:
        count_by_group[row[0]] = row[1]

    # Find top 5 cities with most donors
    cursor.execute("""
        SELECT city, COUNT(*) as total
        FROM donors
        GROUP BY city
        ORDER BY total DESC
        LIMIT 5
    """)
    city_rows = cursor.fetchall()
    top_cities = []
    for row in city_rows:
        top_cities.append({
            'city':  row[0].title(),
            'count': row[1]
        })

    cursor.close()
    connection.close()

    # Return everything as one dictionary
    return {
        'total':          total_donors,
        'available':      available_donors,
        'unavailable':    total_donors - available_donors,
        'count_by_group': count_by_group,
        'top_cities':     top_cities
    }