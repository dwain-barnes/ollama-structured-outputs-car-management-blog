from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from typing import List, Optional
import ollama
from functools import wraps
import json
from rich import print

app = Flask(__name__)
CORS(app)

class Car(BaseModel):
    make: str
    model: str
    year: Optional[int] = None
    color: str
    body_type: Optional[str] = None
    condition: Optional[str] = None
    features: Optional[List[str]] = None
    modifications: Optional[List[str]] = None
    price: Optional[float] = None
    mileage: Optional[int] = None
    plate_number: str  # Add this line

class CarList(BaseModel):
    cars: List[Car]

# Simple in-memory database
car_database = []

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return decorated_function

def get_year_from_plate_number(plate_number: str) -> int:
    # UK registration year codes and their corresponding date ranges
    uk_reg_dates = {
        "51": 2001, "02": 2002, "52": 2002, "03": 2003, "53": 2003, "04": 2004,
        "54": 2004, "05": 2005, "55": 2005, "06": 2006, "56": 2006, "07": 2007,
        "57": 2007, "08": 2008, "58": 2008, "09": 2009, "59": 2009, "10": 2010,
        "60": 2010, "11": 2011, "61": 2011, "12": 2012, "62": 2012, "13": 2013,
        "63": 2013, "14": 2014, "64": 2014, "15": 2015, "65": 2015, "16": 2016,
        "66": 2016, "17": 2017, "67": 2017, "18": 2018, "68": 2018, "19": 2019,
        "69": 2019, "20": 2020, "70": 2020, "21": 2021, "71": 2021, "22": 2022,
        "72": 2022, "23": 2023, "73": 2023, "24": 2024, "74": 2024, "25": 2025,
        "75": 2025, "26": 2026, "76": 2026, "27": 2027, "77": 2027, "28": 2028,
        "78": 2028, "29": 2029, "79": 2029, "30": 2030, "80": 2030
    }
    
    # Extract the numerical part from the plate
    import re
    match = re.search(r'[A-Z]{2}(\d{2})', plate_number)
    if match:
        plate_year = match.group(1)
        return uk_reg_dates.get(plate_year)
    return None

def analyze_cars_in_image(image_path: str) -> CarList:
    response = ollama.chat(
        messages=[
            {
                'role': 'user',
                'content': '''Analyze this image and identify all vehicles present. For each car:
                - Make and model
                - Registration plate number if visible (format: XX## XXX)
                - Color
                - Body type (sedan, SUV, truck, etc.)
                - Visible condition
                - Notable features (sunroof, spoiler, rims, etc.)
                - Any visible modifications
                Pay special attention to the registration plate format.
                Return the complete plate number if visible.''',
                'images': [image_path],
            }
      
        ],
        model='llama3.2-vision:11b-instruct-fp16',
        format=CarList.model_json_schema(),
        options={'temperature': 0}
    )
    
    cars_data = CarList.model_validate_json(response.message.content)
    
    # Process each car to determine year from plate
    processed_cars = []
    for car in cars_data.cars:
        if hasattr(car, 'plate_number') and car.plate_number:
            year = get_year_from_plate_number(car.plate_number)
            if year:
                car.year = year
        processed_cars.append(car)
    
    return CarList(cars=processed_cars)

@app.route('/cars', methods=['POST', 'OPTIONS'])
@handle_errors
def add_car():
    """Add a new car using natural language description"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    description = data.get('description', '')
    
    response = ollama.chat(
        messages=[{
            'role': 'user',
            'content': f'''Extract car information from this text.
            Pay special attention to UK registration plates which indicate the car's year.
            Format is XX## XXX where ## indicates year:
            - First half of year: March to August - number is the year (e.g., 22 = 2022)
            - Second half of year: September to February - number is year plus 50 (e.g., 72 = 2022)
            Include:
            - Make and model
            - Registration number if mentioned
            - Color
            - Body type
            - Features
            
            Text: {description}'''
        }],
        model='llama3.2:3B',
        format=Car.model_json_schema()
    )
    
    car_data = json.loads(response.message.content)
    
    # If plate number is provided, get the year
    if 'plate_number' in car_data:
        year = get_year_from_plate_number(car_data['plate_number'])
        if year:
            car_data['year'] = year
    
    car = Car(**car_data)
    car_database.append(car.model_dump())
    
    return jsonify(car.model_dump()), 201

@app.route('/cars/analyze-image', methods=['POST', 'OPTIONS'])
@handle_errors
def analyze_car_image():
    """Analyze cars in an uploaded image"""
    if request.method == 'OPTIONS':
        return '', 204
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Save the uploaded image temporarily
    image_path = f"temp_{image.filename}"
    image.save(image_path)
    
    try:
        cars_result = analyze_cars_in_image(image_path)
        # Optionally add detected cars to database
        for car in cars_result.cars:
            car_database.append(car.model_dump())
        return jsonify(cars_result.model_dump()), 200
    finally:
        # Cleanup temporary file
        import os
        if os.path.exists(image_path):
            os.remove(image_path)

@app.route('/cars', methods=['GET'])
@handle_errors
def get_cars():
    """Get all cars from the database"""
    return jsonify(car_database)

@app.route('/cars/<make>', methods=['GET'])
@handle_errors
def get_cars_by_make(make):
    """Get all cars of a specific make"""
    cars = [car for car in car_database if car['make'].lower() == make.lower()]
    return jsonify(cars)

if __name__ == '__main__':
    app.run(debug=True)