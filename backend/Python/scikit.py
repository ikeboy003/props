from helpers.helpers import *
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers.legacy import Adam
import tensorflow as tensorflow
import numpy as np
import random as python_random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def perform_analysis(player_id):
    def reset_random_seeds():
       
        np.random.seed(2023)
        python_random.seed(2023)
    

    log , status = helper_get_player_current_season_log(player_id)
    if status != 200:
        return
    
    df = pd.DataFrame(log)

    # Assuming `df` is your DataFrame and it already includes the features and target variable
    # Example features
    features = ['minutes', 'fg_pct', 'fg3_pct',"ft_pct","fg3a","fga","fgm","fg3m"]


    X = df[features]
    y = df['points']

    # Initialize dictionary to store the confidence intervals
    ci_bounds = {}

    # Number of bootstrap samples
    n_bootstrap_samples = 1000

    for feature in features:
        bootstrap_means = []
        for _ in range(n_bootstrap_samples):
         
            bootstrap_sample = X[feature].sample(n=len(X), replace=True)
            bootstrap_means.append(bootstrap_sample.mean())
        
        # Calculate the 5th and 95th percentiles
        lower_bound = np.percentile(bootstrap_means, 5)
        upper_bound = np.percentile(bootstrap_means, 95)
        
   
        ci_bounds[feature] = (lower_bound, upper_bound)

    # Display the 90% confidence intervals for each feature
    for feature, bounds in ci_bounds.items():
        print(f"{feature}: 90% CI = {bounds[0]:.2f} to {bounds[1]:.2f}")

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)

    # Initialize Ridge and Lasso regression models
    ridge_model = Ridge(alpha=1.0)
    lasso_model = Lasso(alpha=0.1)

    # Fit the models to the training data
    ridge_model.fit(X_train, y_train)
    lasso_model.fit(X_train, y_train)

    # Predict on the testing set
    ridge_predictions = ridge_model.predict(X_test)
    lasso_predictions = lasso_model.predict(X_test)

    # Evaluate the models
    ridge_mae = mean_absolute_error(y_test, ridge_predictions)
    lasso_mae = mean_absolute_error(y_test, lasso_predictions)

    ridge_mse = mean_squared_error(y_test, ridge_predictions)
    lasso_mse = mean_squared_error(y_test, lasso_predictions)

    print(f"Ridge MAE: {ridge_mae}, MSE: {ridge_mse}")
    print(f"Lasso MAE: {lasso_mae}, MSE: {lasso_mse}")

    X_example = df[features].mean().to_frame().T  # Convert mean series to DataFrame and transpose

    # Adjust the feature values to the lower bounds of the CI
    X_lower_bound = X_example.copy()
    X_upper_bound = X_example.copy()
    for feature in features:
        X_lower_bound[feature] = ci_bounds[feature][0] 
        X_upper_bound[feature] = ci_bounds[feature][1]# Use the lower bound for each feature

    X_avg = X.mean().to_frame().T 

    mlp_model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', max_iter=10000)

    # Fit the model to the training data
    mlp_model.fit(X_train, y_train)

    # Predict on the testing set
    mlp_predictions = mlp_model.predict(X_test)
    # Predict using the Lasso model with adjusted feature values
    lasso_pred_lower = lasso_model.predict(X_lower_bound)[0]
    lasso_pred_upper = lasso_model.predict(X_upper_bound)[0]

    # Predict using the Ridge model with adjusted feature values
    ridge_pred_lower = ridge_model.predict(X_lower_bound)[0]
    ridge_pred_upper = ridge_model.predict(X_upper_bound)[0]

    # Predict using the MLP model with adjusted feature values
    mlp_pred_lower = mlp_model.predict(X_lower_bound)[0]
    mlp_pred_upper = mlp_model.predict(X_upper_bound)[0]
    ridge_pred_avg = ridge_model.predict(X_avg)[0]
    lasso_pred_avg = lasso_model.predict(X_avg)[0]
    mlp_pred_avg = mlp_model.predict(X_avg)[0]
    # Print the predictions for each model using lower and upper bounds of CI
    print(f"Lasso Prediction with Lower Bounds of CI: {lasso_pred_lower}")
    print(f"Lasso Prediction with Average of Features: {lasso_pred_avg}")
    print(f"Lasso Prediction with Upper Bounds of CI: {lasso_pred_upper}\n")

    print(f"Ridge Prediction with Lower Bounds of CI: {ridge_pred_lower}")
    print(f"Ridge Prediction with Average of Features: {ridge_pred_avg}")
    print(f"Ridge Prediction with Upper Bounds of CI: {ridge_pred_upper}\n")

    print(f"MLP Prediction with Lower Bounds of CI: {mlp_pred_lower}")
    print(f"MLP Prediction with Average of Features: {mlp_pred_avg}")
    print(f"MLP Prediction with Upper Bounds of CI: {mlp_pred_upper}")
    
    
    # Evaluate the model
    average_lower = np.mean([lasso_pred_lower, ridge_pred_lower, mlp_pred_lower])
    average_upper = np.mean([lasso_pred_upper, ridge_pred_upper, mlp_pred_upper])
    average_avg = np.mean([lasso_pred_avg, ridge_pred_avg, mlp_pred_avg])
    print(f"\nAverage Prediction with Lower Bounds of CI across models: {average_lower:.2f}")
    print(f"Average Prediction with Feature Averages across models: {average_avg:.2f}")
    print(f"Average Prediction with Upper Bounds of CI across models: {average_upper:.2f}")
    mlp_mae = mean_absolute_error(y_test, mlp_predictions)
    mlp_mse = mean_squared_error(y_test, mlp_predictions)

    print(f"MLP MAE: {mlp_mae}, MSE: {mlp_mse}")


    # Extract features for all games
    X_all = df[features]

    # Make predictions for all games using each model
    ridge_all_predictions = ridge_model.predict(X_all)

    lasso_all_predictions = lasso_model.predict(X_all)

    mlp_all_predictions = mlp_model.predict(X_all)


    # Actual points for all games
    y_all = df['points'].values


    # Create a DataFrame to compare actual points and predictions
    results_df = pd.DataFrame({
        'Actual Points': y_all,
        'Ridge Predicted Points': ridge_all_predictions,
        'Lasso Predicted Points': lasso_all_predictions,
        'MLP Predicted Points': mlp_all_predictions
    })

    # Initialize counters for each model
    ridge_correct_count = 0
    lasso_correct_count = 0
    mlp_correct_count = 0
    deep_learning_correct_count = 0
    total_games = len(results_df)


    # Define the model
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.1),
        Dense(64, activation='relu'),
        Dense(1)  # Output layer for regression
    ])

    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=100, batch_size=10, validation_split=0.1, verbose=0)
    # Predict the points for all games using the deep learning model
    deep_learning_predictions = model.predict(X_all).flatten()

    # Make sure this line is correctly executed
    results_df['Deep Learning Predicted Points'] = deep_learning_predictions

    for index, row in results_df.iterrows():
        actual_points = row['Actual Points']
        ridge_pred = round(row['Ridge Predicted Points'])
        lasso_pred = round(row['Lasso Predicted Points'])
        mlp_pred = round(row['MLP Predicted Points'])
        deep_learning_pred = round(row['Deep Learning Predicted Points'])
        
        # Check if the rounded prediction is greater than or equal to the actual points for each model
        if ridge_pred >= actual_points:
            ridge_correct_count += 1
        if lasso_pred >= actual_points:
            lasso_correct_count += 1
        if mlp_pred >= actual_points:
            mlp_correct_count += 1
        if deep_learning_pred >= actual_points:
            deep_learning_correct_count += 1


    ridge_accuracy_percentage = (ridge_correct_count / total_games) * 100
    lasso_accuracy_percentage = (lasso_correct_count / total_games) * 100
    mlp_accuracy_percentage = (mlp_correct_count / total_games) * 100
    deep_learning_accuracy_percentage = (deep_learning_correct_count / total_games) * 100


    # Print the results
    print(f"Ridge model was most correct in {ridge_accuracy_percentage:.2f}% of the games.")
    print(f"Lasso model was most correct in {lasso_accuracy_percentage:.2f}% of the games.")
    print(f"MLP model was most correct in {mlp_accuracy_percentage:.2f}% of the games.")
    print(f"Deep Learning model was most correct in {deep_learning_accuracy_percentage:.2f}% of the games.")


@app.route('/analyze', methods=['GET'])
def analyze_player():
    player_id = request.args.get('player_id')
    if not player_id:
        return jsonify({'error': 'Missing player_id parameter'}), 400

    try:
        analysis_result = perform_analysis(player_id)
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app.run(debug=True, port=1234)