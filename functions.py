from geopandas.tools import geocode
import folium
import warnings
import pandas as pd
from geopandas.tools import geocode

warnings.filterwarnings("ignore", category=DeprecationWarning)
wonders = ['Taj Mahal', 'Colosseum', 'Machu Picchu', 'Christ the Redeemer', 'Chichen Itza', 'petra']

df = pd.DataFrame({'wonders': wonders})


def custom_geocoder(address):
    dataframe = geocode(address, provider="nominatim", user_agent='my_request')
    point = dataframe.geometry.iloc[0]
    return pd.Series({'Latitude': point.y, 'Longitude': point.x})


def getMapFromAdress(adress):
    return 0


df[['latitude', 'longitude']] = df.wonders.apply(lambda x: custom_geocoder(x))
df

mapit = folium.Map( location=[0, 0], zoom_start=1 )
for lat , lon in zip(df.latitude , df.longitude):
    folium.Marker( location=[ lat,lon ], fill_color='#43d9de',
                   radius=8 ).add_to( mapit )
mapit