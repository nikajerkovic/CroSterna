from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import json
import os

app = Flask(__name__)

# Load models and data
models_path = 'static/'
base_model = joblib.load(os.path.join(models_path, 'base_model.pkl'))
logistic_models = {
    '30_lower': joblib.load(os.path.join(models_path, '30_lower.pkl')),
    '30_upper': joblib.load(os.path.join(models_path, '30_upper.pkl')),
    '40_lower': joblib.load(os.path.join(models_path, '40_lower.pkl')),
    '40_upper': joblib.load(os.path.join(models_path, '40_upper.pkl')),
    '50_lower': joblib.load(os.path.join(models_path, '50_lower.pkl')),
    '50_upper': joblib.load(os.path.join(models_path, '50_upper.pkl')),
    '60_lower': joblib.load(os.path.join(models_path, '60_lower.pkl')),
    '60_upper': joblib.load(os.path.join(models_path, '60_upper.pkl')),
    '70_lower': joblib.load(os.path.join(models_path, '70_lower.pkl')),
    '70_upper': joblib.load(os.path.join(models_path, '70_upper.pkl'))
}

with open(os.path.join(models_path, 'std_dev.json'), 'r') as f:
    std_dev_data = json.load(f)
std_dev = std_dev_data['std_dev']

features_for_logistic_models = {
    '30_lower': ['OS'],
    '30_upper': ['FX', 'OS', 'Sex_encoded'],
    '40_lower': ['OS', 'Sex_encoded'],
    '40_upper': ['FX', 'OR', 'OS', 'Sex_encoded'],
    '50_lower': ['OS', 'Sex_encoded'],
    '50_upper': ['OS'],
    '60_lower': ['OR'],
    '60_upper': ['OR', 'Sex_encoded'],
    '70_lower': ['OR'],
    '70_upper': ['OR']
}

def adjust_prediction_interval(x_i, lower_bound, upper_bound, logistic_models, features_for_each_model):
    if lower_bound < 18:
        lower_bound = 18
    if 18 <= lower_bound < 30:
        if logistic_models['30_lower'].predict(x_i[features_for_each_model['30_lower']])[0] == 1 and \
           logistic_models['40_lower'].predict(x_i[features_for_each_model['40_lower']])[0] == 1:
            lower_bound = 30
    elif 30 <= lower_bound < 40:
        if logistic_models['40_lower'].predict(x_i[features_for_each_model['40_lower']])[0] == 1 and \
           logistic_models['50_lower'].predict(x_i[features_for_each_model['50_lower']])[0] == 1 and \
           logistic_models['60_lower'].predict(x_i[features_for_each_model['60_lower']])[0] == 1:
            lower_bound = 40
    if lower_bound < 30:
        if logistic_models['30_upper'].predict(x_i[features_for_each_model['30_upper']])[0] == 0 and \
           logistic_models['40_upper'].predict(x_i[features_for_each_model['40_upper']])[0] == 0:
            upper_bound = 40
    if 70 <= upper_bound < 75:
        if logistic_models['50_upper'].predict(x_i[features_for_each_model['50_upper']])[0] == 0 and \
           logistic_models['60_upper'].predict(x_i[features_for_each_model['60_upper']])[0] == 0 and \
           logistic_models['70_upper'].predict(x_i[features_for_each_model['70_upper']])[0] == 0:
            upper_bound = 70
    #elif 75 <= upper_bound < 100:
    #   if logistic_models['70_upper'].predict(x_i[features_for_each_model['70_upper']])[0] == 0 and \
    #     logistic_models['60_upper'].predict(x_i[features_for_each_model['60_upper']])[0] == 0:
    #     upper_bound = 70
    return lower_bound, upper_bound

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        FX = request.form['FX']
        OR = request.form['OR']
        OS = request.form['OS']
        Sex = request.form['Sex']

        # Validate input
        if not FX or not OR or not OS or not Sex:
            return jsonify({"warning": "Please fill all the fields before predicting."}), 200

        try:
            FX = int(FX)
            OR = int(OR)
            OS = int(OS)
            if Sex.lower() not in ['m', 'f']:
                raise ValueError("Invalid sex")
            Sex = 1 if Sex.lower() == 'm' else 0
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        x = pd.DataFrame({'FX': [FX], 'OR': [OR], 'OS': [OS], 'Sex_encoded': [Sex]})
        lower_bound = base_model.predict(x)[0] -  1.96 * std_dev
        upper_bound = base_model.predict(x)[0] +  1.96 * std_dev
        adjusted_lower, adjusted_upper = adjust_prediction_interval(
            x, lower_bound, upper_bound, logistic_models, features_for_logistic_models)

        lower_bound_percentage = ((adjusted_lower - 18) / (100 - 18)) * 100
        upper_bound_percentage = ((adjusted_upper - 18) / (100 - 18)) * 100
        range_width_percentage = upper_bound_percentage - lower_bound_percentage
        adjusted_lower = round(adjusted_lower, 2)
        adjusted_upper = round(adjusted_upper, 2)

        result = {
            'adjusted_lower': adjusted_lower,
            'adjusted_upper': adjusted_upper,
            'lower_bound_percentage': lower_bound_percentage,
            'upper_bound_percentage': upper_bound_percentage,
            'range_width_percentage': range_width_percentage
        }

        return jsonify(result), 200
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
