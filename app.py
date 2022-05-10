import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
from sklearn.preprocessing import OneHotEncoder
import xgboost as xgb
import sys
from xgboost import XGBClassifier, XGBRFClassifier

# Create flask app
flask_app = Flask(__name__)
model = pickle.load(open("xgb_clf_nft.pkl", "rb"))

@flask_app.route("/")
def Home():
    return render_template("index.html")

@flask_app.route("/predict", methods=['GET', 'POST'])
def predict():
    np.set_printoptions(threshold=sys.maxsize)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    
    float_features = [x for x in request.form.values()]
    features = [np.array(float_features)]
    #change the date format for evaluation of the ml model
    sep ='/'
    features[0][0] = sep.join(features[0][0].split('-')[::-1])
    features[0][3] = sep.join(features[0][3].split('-')[::-1])
    #transform to dataframe pandas
    features_df = pd.DataFrame(features, columns = ['mint date','supply (nuber of nfts)','mint price','twitter account creation month','total discord members','active discord members','twitter followers','art category'])
    #preprocess
    features = preprocessing(features_df)
    
    prediction = model.predict(features)
    #prediction = 0
    if prediction ==1:
        prediction=''
    else :
        prediction = 'not'
        
    return render_template("index.html", prediction_text = "Prediction: the collection will probably {} sell out".format(prediction))


def categorial_feature_handling(feature_dataframe):
    """
Encodes categorical features like 'art category' to a numerical representation.
    """ 
    enc = OneHotEncoder()
    encoded_art_category = enc.fit_transform(np.asarray(feature_dataframe["art category"]).reshape(-1,1))
    feature_dataframe["art category"] = encoded_art_category.toarray()
    return feature_dataframe


def feature_removal_and_data_cleaning(feature_dataframe):
    """
Data cleaning to handle rows with inconsistent values or in the wrong domain. 

Drop features that do not provide a strong signal in determining our label (whether a collection
sells out or what the floor price is).
    """
    #relevant_features = feature_dataframe.drop(columns = ["Name of the project", "marketplace", "website link", "twitter account creation month", "mint date"])
    relevant_features = feature_dataframe.drop(columns = [ "twitter account creation month", "mint date"])
    feature_dataframe["mint date"] = feature_dataframe["mint date"].apply(lambda x:str(x).strip().lower().replace(' ', ''))
    feature_dataframe["twitter account creation month"] = feature_dataframe["twitter account creation month"].apply(lambda x:str(x).strip().lower().replace(' ', ''))
    try:
        relevant_features["hype_window"] = pd.to_datetime("01/" + feature_dataframe["twitter account creation month"], format = "%d/%m/%y", exact= False, errors = "coerce") - pd.to_datetime(feature_dataframe["mint date"], format = "%d/%m/%y", exact= False, errors = "coerce") 
    except ValueError:
        relevant_features["hype_window"] = pd.to_datetime("01/" + feature_dataframe["twitter account creation month"], format = "%d/%m/%y", exact= False, errors = "coerce") - pd.to_datetime("01/" + feature_dataframe["mint date"], format =  "%d/%m/%y", exact= False)
    relevant_features["hype_window"] = relevant_features["hype_window"].apply(lambda x: float(np.abs(x.days)))
    
    relevant_features["art category"] = relevant_features["art category"].apply(lambda x:str(x).strip().lower())
    
    relevant_features["supply (nuber of nfts)"] = relevant_features["supply (nuber of nfts)"].replace("300+", "3000")
    relevant_features["supply (nuber of nfts)"] = relevant_features["supply (nuber of nfts)"].apply(lambda x: float(str(x).replace(',','').replace(' ', '')))
    
    relevant_features["total discord members"] = relevant_features["total discord members"].apply(lambda x: float(str(x).replace(',','').replace(' ', '')))
    relevant_features["active discord members"] = relevant_features["active discord members"].apply(lambda x: float(str(x).replace(',','').replace(' ', '')))
    
    relevant_features["twitter followers"] = relevant_features["twitter followers"].apply(lambda x:str(x).strip().lower().replace(' ', ''))
    relevant_features["twitter followers"] = relevant_features["twitter followers"].apply(lambda x: str(x).replace(',','').replace(' ', ''))
    relevant_features["twitter followers"] = relevant_features["twitter followers"].replace('8922f', '8922')
    relevant_features["twitter followers"] = relevant_features["twitter followers"].replace(r'[k]+$', '', regex=True).astype(float) * relevant_features["twitter followers"].str.extract(r'[\d\.]+([k]+)', expand=False).fillna(1).replace('k', 10**3).astype(int)


    
    relevant_features["mint price"] = relevant_features["mint price"].replace("0.05 – 0.18", "0.925")
    relevant_features["mint price"] = relevant_features["mint price"].replace("1-2", "1.5")
    relevant_features["mint price"] = relevant_features["mint price"].replace("08/21", np.nan)
    relevant_features["mint price"] = relevant_features["mint price"].replace("0.85 SOL - 1.2 SOL", "1.025")
    relevant_features["mint price"] = relevant_features["mint price"].apply(lambda x:str(x).strip().lower())
    relevant_features["mint price"] = relevant_features["mint price"].replace(["free", "free mint"], "0")

    relevant_features["mint price"] = relevant_features["mint price"].apply(lambda x: float(str(x).replace(',','.').replace(' ', '')))


    relevant_features["art category"] = relevant_features["art category"].replace("carttoon", "cartoon")
    relevant_features["art category"] = relevant_features["art category"].replace(["photography", "photo"], "photos")
    relevant_features["art category"] = relevant_features["art category"].replace("2d art", "2d")
    relevant_features["art category"] = relevant_features["art category"].replace(["3d art", "3d cartoon"], "3d")
    relevant_features["art category"] = relevant_features["art category"].replace(["collectible", "design", "pixel art", "drawing", "metaverse", "painting",
    "graphics", "nan", "physical", "video", "print", "hand painted"], "other")

    return relevant_features

def preprocessing(input_vector: pd.DataFrame):
    input_vector = feature_removal_and_data_cleaning(input_vector)
    input_vector = categorial_feature_handling(input_vector)
    return input_vector

if __name__ == "__main__":
    flask_app.run(debug=True)