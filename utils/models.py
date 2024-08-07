from joblib import load

path = 'models/rf/'
resales_model = load(path + 'random_forest_resales.joblib')
rentals_model = load(path + 'random_forest_rentals.joblib')
