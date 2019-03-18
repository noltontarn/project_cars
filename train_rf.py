import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA

X1 = np.load("data/X_m.npy")
y1 = np.load("data/y_m.npy")
X2 = np.load("data/X_m2.npy")
y2 = np.load("data/y_m2.npy")
X3 = np.load("data/X_m3.npy")
y3 = np.load("data/y_m3.npy")

X = np.concatenate((X1, X2, X3))
y = np.concatenate((y1, y2, y3))

print(X.shape)
scaler = StandardScaler()
X = scaler.fit_transform([i.flatten() for i in X])
print(X.shape)

pca = PCA(n_components = 100)
X = pca.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)
print("data splitted")

model = RandomForestRegressor(n_estimators = 100)
print("training...")
model = model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(acc)