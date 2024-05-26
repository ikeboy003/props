from sklearn.decomposition import PCA
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
from helpers.helpers import *

df = get_player_log_df("1627783")
df['MATCHUP'] = df['MATCHUP'].apply(lambda x: 1 if '@' in x else 2)


features = df.select_dtypes(include=[np.number]).columns.tolist()

features.remove("REB")
features.remove("DREB")
features.remove("OREB")
X = df[features]

y = df['REB']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=0.95)  
X_pca = pca.fit_transform(X_scaled)

lasso = LassoCV(cv=5)
lasso.fit(X_pca, y)
coef = lasso.coef_
index = np.where(coef != 0)[0]  
X_lasso = X_pca[:, index]

rf = RandomForestRegressor(n_estimators=100)
rf.fit(X_lasso, y)
importances = rf.feature_importances_

rf_direct = RandomForestRegressor(n_estimators=100)
rf_direct.fit(X_scaled, y)
direct_importances = rf_direct.feature_importances_


feature_importance_mapping = {feature: importance for feature, importance in zip(features, direct_importances)}
print(feature_importance_mapping)

# Sort the feature importances by importance in descending order
sorted_feature_importances = sorted(feature_importance_mapping.items(), key=lambda x: x[1], reverse=True)

# Print sorted feature importances
for feature, importance in sorted_feature_importances:
    print(f"{feature}: {importance}")
