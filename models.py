from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import (
    r2_score, mean_squared_error,
    accuracy_score, confusion_matrix,
    precision_score, recall_score
)

def run_model(df, model_name, features, target):
    X = df[features]
    y = df[target]

    # Selección del modelo
    if model_name == 'linear_regression':
        model = LinearRegression()
    elif model_name == 'logistic_regression':
        model = LogisticRegression(max_iter=1000)
    elif model_name == 'kmeans':
        model = KMeans(n_clusters=3)
    elif model_name == 'decision_tree':
        model = DecisionTreeClassifier() if y.dtype == 'object' else DecisionTreeRegressor()
    elif model_name == 'svm':
        model = SVC() if y.dtype == 'object' else SVR()
    elif model_name == 'mlp':
        model = MLPClassifier(max_iter=500) if y.dtype == 'object' else MLPRegressor(max_iter=500)
    else:
        raise ValueError(f'Modelo no soportado: {model_name}')

    # Entrenamiento
    model.fit(X, y)
    preds = model.predict(X)
    results = {}

    # Parámetros del modelo
    if hasattr(model, 'coef_'):
        results['coefficients'] = model.coef_.tolist()
    if hasattr(model, 'intercept_'):
        intercept = model.intercept_
        # Asegurar que sea lista para uniformidad
        results['intercept'] = intercept.tolist() if hasattr(intercept, 'tolist') else float(intercept)
    if hasattr(model, 'cluster_centers_'):
        results['centroids'] = model.cluster_centers_.tolist()

    # Agregar datos para visualización
    results['actual'] = y.tolist()
    results['predictions'] = preds.tolist()
    results['feature_names'] = features

    # Métricas de desempeño
    if y.dtype != 'object':  # Regresión
        results['r2'] = r2_score(y, preds)
        results['mse'] = mean_squared_error(y, preds)
    else:  # Clasificación
        results['accuracy'] = accuracy_score(y, preds)
        results['confusion_matrix'] = confusion_matrix(y, preds).tolist()
        results['precision'] = precision_score(y, preds, average='macro')
        results['recall'] = recall_score(y, preds, average='macro')

    return results