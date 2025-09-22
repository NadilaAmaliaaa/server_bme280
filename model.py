from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib

# Load data
data = pd.read_csv('smart_farm_zoning_dataset.csv')
X = data[['temperature', 'pressure', 'altitude']]
y = data['zone_class']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standarisasi
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Latih model
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_scaled, y_train)

# Simpan model dan scaler
joblib.dump(knn, 'knn_model01.pkl')
joblib.dump(scaler, 'scaler.pkl')

# Evaluasi di training set
y_train_pred = knn.predict(X_train_scaled)
train_acc = accuracy_score(y_train, y_train_pred)

# Evaluasi di testing set
y_test_pred = knn.predict(X_test_scaled)
test_acc = accuracy_score(y_test, y_test_pred)

print("Training Accuracy:", train_acc)
print("Testing Accuracy :", test_acc)

# Load model dan scaler
model = joblib.load('knn_model01.pkl')
scaler = joblib.load('scaler.pkl')

# Data baru: [temperature, pressure, altitude]
data_baru = [[30.5, 1013.25, 10.0]]

# Standarisasi data baru
data_baru_scaled = scaler.transform(data_baru)

# Prediksi
prediksi = model.predict(data_baru_scaled)
print("Hasil Prediksi:", prediksi[0])
