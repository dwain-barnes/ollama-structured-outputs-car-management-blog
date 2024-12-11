# Ollama Structured Outputs - Car Management Example

This repository demonstrates how to use **Ollama's Structured Outputs** to create a Car Management System. 
The examples highlight extracting structured data from natural language descriptions and analysing car details from images using predefined JSON schemas.
It was written as a blog. 

## Key Features

- **Structured Outputs**: Ensure consistent and reliable AI responses using JSON schemas.
- **Text Input**: Extract car details like make, model, year, and registration plate from textual descriptions.
- **Image Analysis**: Analyze images of cars to identify make, model, color, and other details.
- **Python Integration**: Built with Flask and Pydantic for seamless schema validation.

## Getting Started

### Prerequisites

Ensure you have **Python 3.11** and Conda installed on your machine.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dwain-barnes/ollama-structured-outputs-car-management-blog.git
   cd ollama-structured-outputs-car-management-blog
   ```

2. Create and activate a Conda environment:
   ```bash
   conda create -n structured_output python=3.11
   conda activate structured_output
   ```

3. Install dependencies:
   ```bash
   pip install flask flask-cors pydantic ollama rich python-multipart
   ```

4. Run the application:
   ```bash
   python structured_outputs.py
   ```

The application will be accessible at `http://127.0.0.1:5000`.
You can now run the main.html for a web front end interface.

## Repository Structure

```
.
├── main.html                # Frontend interface for the Car Management System
├── structured_outputs.py    # Backend server using Flask and Ollama
├── example_car.jpg          # Sample car image for image analysis
├── README.md                # Project documentation
```

## Example Usage

### Text Description Input

Send a POST request with a car description to extract structured car details:
```bash
curl -X POST http://127.0.0.1:5000/cars \
     -H "Content-Type: application/json" \
     -d '{"description": "A red Tesla Model 3 registration number RF22 HTG."}'
```

Response:
```json
{
  "make": "Tesla",
  "model": "Model 3",
  "year": 2022,
  "color": "red",
  "plate_number": "RF22 HTG"
}
```

### Image Upload

Upload a car image to extract structured details:
```bash
curl -X POST http://127.0.0.1:5000/cars/analyze-image \
     -F "image=@example_car.jpg"
```

Response:
```json
{
  "make": "Toyota",
  "model": "Yaris",
  "color": "blue",
  "plate_number": "GR22 HTG",
  "condition": "good"
}
```
## Learn More

For more details about Ollama's Structured Outputs, check out the [official documentation](https://ollama.ai).
