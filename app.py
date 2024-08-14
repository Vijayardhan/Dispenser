from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Dispenser']
collection = db['receptional_details']
patient_collection = db['Patient_details']  # New collection for patient details

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hospital_name = request.form['hospital_name']
        
        # Check if user exists
        if collection.find_one({'username': username}):
            return 'User already exists!'
        
        collection.insert_one({'username': username, 'password': password, 'hospital_name': hospital_name})
        return redirect(url_for('signin'))
    
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = collection.find_one({'username': username})
        
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        elif not user:
            return "<script>alert('Kindly signup'); window.location.href='/signup';</script>"
        else:
            return "<script>alert('Invalid credentials!'); window.location.href='/signin';</script>"
    
    return render_template('signin.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    return redirect(url_for('signin'))

@app.route('/submit_patient_details', methods=['POST'])
def submit_patient_details():
    if 'username' in session:
        if request.method == 'POST':
            patient_name = request.form['patient_name']
            phone_number = request.form['phone_number']
            location = request.form['location']
            sickness = request.form['sickness']

            # Generate a 4-digit random ID
            patient_id = f"{random.randint(1000, 9999)}: {patient_name}"
            
            # Store the details in the database
            patient_data = {
                'patient_id': patient_id,
                'patient_name': patient_name,
                'phone_number': phone_number,
                'location': location,
                'sickness': sickness
            }
            patient_collection.insert_one(patient_data)
            
            # Return the message with the ID
            return render_template('submit_patient_details.html', message=f"Patient details submitted successfully! ID: {patient_id}")

    return redirect(url_for('signin'))

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
