# Define endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get data from request (assuming JSON format)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Check if all required keys are present in the data
    required_keys = ['gender', 'married', 'self_employed', 'credit_history', 'loan_status', 'education', 'property_area']
    if not all(key in data for key in required_keys):
        return jsonify({'error': 'Missing required data fields'}), 400

    # Preprocess data (handle potential missing values, etc.)
    # ... (consider using a validation schema or data cleaning techniques)

    # Encode categorical features using loaded encoders
    encoded_data = []
    encoded_data.append(label_gen.transform([data['gender']])[0])
    encoded_data.append(label_marr.transform([data['married']])[0])
    encoded_data.append(label_self.transform([data['self_employed']])[0])
    encoded_data.append(label_credit.transform([data['credit_history']])[0])
    encoded_data.append(label_status.transform([data['loan_status']])[0])
    encoded_data.append(label_edu.transform([data['educatio']])[0])
    encoded_data.append(label_proA.transform([data['property_area']])[0])
    # ... encode other features using their respective encoders

    # Perform prediction using the model
    prediction = model.predict([encoded_data])

    # Return the prediction
    return jsonify({'prediction': prediction.tolist()})
