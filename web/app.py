from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )
    return conn

# Helper function to fetch all rows from the database
def fetch_all_rows():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM mytable")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.route("/", methods=["GET"])
def index():
    # Fetch all rows from the database
    rows = fetch_all_rows()
    return render_template("index.html", rows=rows)

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form['username']
    password = request.form['password']
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO mytable (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()

        # Fetch updated data to return to the client
        rows = fetch_all_rows()

        return jsonify({"message": "User created successfully!", "rows": rows, "status": "success"})
    
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Query the database to check if the username and password match
        cur.execute("SELECT * FROM mytable WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()

        # Close the connection
        cur.close()
        conn.close()

        if user:
            message = f"Connection Successful for user: {username}"
            return jsonify({"message": message, "status": "success", "rows": fetch_all_rows()})
        else:
            message = "Invalid username or password"
            return jsonify({"message": message, "status": "error", "rows": fetch_all_rows()})
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error during login: {str(e)}")
        return jsonify({"message": "An error occurred. Please try again.", "status": "error", "rows": fetch_all_rows()})

@app.route("/delete_row", methods=["POST"])

def delete_row():
    username = request.form['username']
    password = request.form['password']
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT * FROM mytable WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        
        if user:
            # Delete the row if it matches
            cur.execute("DELETE FROM mytable WHERE username = %s AND password = %s", (username, password))
            conn.commit()
            result_message = "Row deleted successfully"
            status = "success"
        else:
            result_message = "Invalid username or password"
            status = "error"  # Set the status to "error" when the user doesn't exist
        
        cur.close()
        conn.close()

        # Fetch updated data to return to the client
        rows = fetch_all_rows()
        return jsonify(message=result_message, rows=rows, status=status)
    
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})


@app.route("/delete_all", methods=["POST"])
def delete_all():
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete all rows from the table
        cur.execute("DELETE FROM mytable")
        
        # Reset the sequence for the id column so it starts at 1 again
        cur.execute("ALTER SEQUENCE mytable_id_seq RESTART WITH 1")
        
        conn.commit()

        # Fetch updated data to return to the client (should be empty if all rows were deleted)
        rows = fetch_all_rows()

        # Close connections
        cur.close()
        conn.close()

        # Return a response with a message and the updated rows
        return jsonify(message="All rows deleted successfully", rows=rows, status="success")
    
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
