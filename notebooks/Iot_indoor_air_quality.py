#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ===========================
# IMPORTS & CONFIG
# ===========================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

plt.style.use("ggplot")
sns.set_context("talk")

print("Imports OK ✔️")


# 

# 

# In[ ]:


# ===========================
# LOAD DATASET
# ===========================
df = pd.read_csv("../app/data/IoT_Indoor_Air_Quality_Dataset.csv")
print("Dataset chargé ✔️")
display(df.head())
print(df.info())


# 

# In[ ]:


# ===========================
# CLEANING & PREPROCESSING
# ===========================
# Conversion Timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Timestamp"])
print("✔️ Timestamp nettoyé")

# Suppression des valeurs aberrantes (IQR)
numeric_cols = ["Temperature (?C)", "Humidity (%)", "CO2 (ppm)",
                "PM2.5 (?g/m?)", "PM10 (?g/m?)", "TVOC (ppb)", "Occupancy Count"]

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    df = df[(df[col] >= lower) & (df[col] <= upper)]

print("✔️ Valeurs aberrantes supprimées")

# In[ ]:


# ===========================
# AQI INTERIEUR PERSONNALISE
# ===========================
def compute_indoor_aqi(row):
    score = 0
    # Pollution (OMS)
    score += row["PM2.5 (?g/m?)"] / 35
    score += row["PM10 (?g/m?)"] / 50
    score += row["CO2 (ppm)"] / 1000
    score += row["TVOC (ppb)"] / 220
    # Confort thermique
    score += max(0, abs(row["Temperature (?C)"] - 22)/4)
    score += max(0, abs(row["Humidity (%)"] - 50)/10)
    # Présence
    score += row["Occupancy Count"]/20
    return score

df["AQI_Indoor"] = df.apply(compute_indoor_aqi, axis=1)

# Création de labels basés sur percentiles
percentiles = np.percentile(df["AQI_Indoor"], [33, 66])
df["AQI_Label"] = pd.cut(df["AQI_Indoor"],
                          bins=[-np.inf, percentiles[0], percentiles[1], np.inf],
                          labels=["Good", "Moderate", "Poor"])
print(df["AQI_Label"].value_counts())


# 

# In[ ]:


# ===========================
# FEATURE ENGINEERING
# ===========================

# Renommage uniquement des colonnes utilisées
df = df.rename(columns={
    "Temperature (?C)": "temperature",
    "Humidity (%)": "humidity",
    "CO2 (ppm)": "co2",
    "PM2.5 (?g/m?)": "pm25",
    "PM10 (?g/m?)": "pm10",
    "TVOC (ppb)": "tvoc",
    "Occupancy Count": "occupancy"
})

features = ["temperature", "humidity", "co2", "pm25", "pm10", "tvoc", "occupancy"]

target = "AQI_Label"

X = df[features]
y = df[target]

print("X shape:", X.shape)
print("y shape:", y.shape)


# In[ ]:


# ===========================
# EXPLORATORY DATA ANALYSIS
# ===========================
plt.figure(figsize=(16,6))
df[features].hist(bins=30, figsize=(16,10))
plt.suptitle("Distribution des capteurs")
plt.show()

corr = df[features + [target]].apply(lambda x: pd.factorize(x)[0] if x.name==target else x).corr()
plt.figure(figsize=(10,8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Matrice de corrélation")
plt.show()


# In[ ]:


# ===========================
# TRAIN / TEST SPLIT
# ===========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("Train size:", X_train.shape, "Test size:", X_test.shape)
print("Répartition des classes:", y_train.value_counts(normalize=True))


# In[ ]:


# ===========================
# MODEL TRAINING
# ===========================
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)
print("✔️ Modèle entraîné")


# In[ ]:


# ===========================
# EVALUATION
# ===========================
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred, labels=["Good","Moderate","Poor"])
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Good","Moderate","Poor"],
            yticklabels=["Good","Moderate","Poor"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()


# In[ ]:


# ===========================
# FEATURE IMPORTANCE
# ===========================
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(12,6))
plt.bar(range(len(importances)), importances[indices])
plt.xticks(range(len(importances)), np.array(features)[indices], rotation=45, ha="right")
plt.title("Importance des features")
plt.show()


# In[ ]:


# ===========================
# SAVE MODEL
# ===========================
joblib.dump(model, "../app/data/indoor_aqi_model.pkl", compress=3)
print("✔️ Modèle sauvegardé sous 'indoor_aqi_model.pkl'")


# In[ ]:


# ===========================
# TESTS DU MODELE (EXEMPLES)
# ===========================

# Exemples de tests avec les colonnes renommées pour le ML
sample_tests = [
    {"temperature": 28.0, "humidity": 70.0, "co2": 1800, "pm25": 80.0, "pm10": 120.0, "tvoc": 400, "occupancy": 50},
    {"temperature": 30.0, "humidity": 50.0, "co2": 500, "pm25": 10.0, "pm10": 15.0, "tvoc": 50, "occupancy": 5},
    # Attendu : Moderate (la température dépasse 26°C)
    {"temperature": 22.0, "humidity": 45.0, "co2": 400, "pm25": 8.0, "pm10": 12.0, "tvoc": 30, "occupancy": 0},
    # Attendu : Good
    {"temperature": 24.0, "humidity": 55.0, "co2": 1200, "pm25": 40.0, "pm10": 60.0, "tvoc": 250, "occupancy": 30}
    # Attendu : Poor ou Moderate selon la combinaison exacte des seuils
]

# Chargement du modèle
loaded_model = joblib.load("../app/data/indoor_aqi_model.pkl")

# Boucle de prédiction
for ex in sample_tests:
    df_ex = pd.DataFrame([ex])
    pred = loaded_model.predict(df_ex)[0]
    print(f"Exemple:\n{df_ex}")
    print(f"➡️ Prédiction AQI_Label: {pred}\n")

