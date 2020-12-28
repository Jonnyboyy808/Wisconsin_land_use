from matplotlib.animation import FuncAnimation
import pandas as pd, io, os, zipfile, csv, numpy as np
from zipfile import ZipFile
from io import TextIOWrapper
from collections import abc
from collections import OrderedDict
from IPython.core.display import display, HTML
from sklearn.linear_model import LinearRegression
import sqlite3, json, math
from matplotlib import pyplot as plt 
from matplotlib.colors import ListedColormap

#In uses, the first column is the land use codes. The other columns are just specific colors for specific codes 
use_cmap = np.zeros(shape=(256,4))
use_cmap[:,-1] = 1
uses = np.array([
    [0, 0.00000000000, 0.00000000000, 0.00000000000],
    [11, 0.27843137255, 0.41960784314, 0.62745098039],
    [12, 0.81960784314, 0.86666666667, 0.97647058824],
    [21, 0.86666666667, 0.78823529412, 0.78823529412],
    [22, 0.84705882353, 0.57647058824, 0.50980392157],
    [23, 0.92941176471, 0.00000000000, 0.00000000000],
    [24, 0.66666666667, 0.00000000000, 0.00000000000],
    [31, 0.69803921569, 0.67843137255, 0.63921568628],
    [41, 0.40784313726, 0.66666666667, 0.38823529412],
    [42, 0.10980392157, 0.38823529412, 0.18823529412],
    [43, 0.70980392157, 0.78823529412, 0.55686274510],
    [51, 0.64705882353, 0.54901960784, 0.18823529412],
    [52, 0.80000000000, 0.72941176471, 0.48627450980],
    [71, 0.88627450980, 0.88627450980, 0.75686274510],
    [72, 0.78823529412, 0.78823529412, 0.46666666667],
    [73, 0.60000000000, 0.75686274510, 0.27843137255],
    [74, 0.46666666667, 0.67843137255, 0.57647058824],
    [81, 0.85882352941, 0.84705882353, 0.23921568628],
    [82, 0.66666666667, 0.43921568628, 0.15686274510],
    [90, 0.72941176471, 0.84705882353, 0.91764705882],
    [95, 0.43921568628, 0.63921568628, 0.72941176471],
])
#Finalized it with a color map 
for row in uses:
    use_cmap[int(row[0]),:-1] = row[1:]
use_cmap = ListedColormap(use_cmap)

#This dictionary uses the land use codes as keys and gives the use code descriptions as the values
use_codes = {11:'Open Water', 12: 'Perennial Ice/Snow', 
               21: "Developed, Open Space", 22: "Developed, Low Intensity",
               23: "Developed, Medium Intensity", 24: "Developed, High Intensity",
               31: "Barren Land (Rock/Sand/Clay)", 41: "Deciduous Forest",
               42: "Evergreen Forest", 43: "Mixed Forest",
               51: "Dwarf Scrub (Alaska)", 52: "Shrub/Scrub",
               71: "Grassland/Herbaceous", 72: "Sedge/Herbaceous (Alaska)",
               73: "Lichens (Alaska)", 74: "Moss (Alaska)",
               81: "Pasture/Hay", 82: "Cultivated Crops",
               90: "Woody Wetlands", 95: "Emergent Herbaceous Wetlands"
               }
#Setting up a sqlite3 connection whenever a Connection class is created.
def open(name):
    c = Connection(name)
    return c 
            
class Connection:
    def __init__(self, name):
        self.name = name
        self.db = sqlite3.connect(name+".db")
        self.zf = zipfile.ZipFile(name+".zip") 
        
        places_df = pd.read_sql("SELECT * FROM places", self.db)
        images_df = pd.read_sql("SELECT * FROM images", self.db)
        places_df.to_sql("places", self.db, if_exists="replace", index=False)
        images_df.to_sql("images", self.db, if_exists="replace", index=False)

        self.df = pd.read_sql("""
              SELECT * FROM 
              images INNER JOIN places 
              ON images.place_id = places.place_id""",
      self.db).drop(columns="place_id")
        
    def __enter__(self):
        return self 
#List images returns an. alphabetically sorted list of images
    def list_images(self):
        lst = self.df["image"].tolist()
        lst = sorted(lst)
        return lst
#Returns the year from the DB corresponding to a specific image.    
    def image_year(self, name):
        for i in range(len(self.df)):
            if self.df["image"][i] == name:
                return int(self.df["year"][i])
#Returns the name from the DB corresponding to a specific image.         
    def image_name(self, name):
        for i in range(len(self.df)):
            if self.df["image"][i] == name:
                return self.df["name"][i]
#Returns a numpy array that encodes area usage.             
    def image_load(self, name):
        with ZipFile("images.zip") as zf:
            with zf.open(name) as f:
                buf = io.BytesIO(f.read())
        area_array = np.load(buf)
        return area_array
#Returns a plot with the "Images year" and "City Name"    
    def plot_img(self, name, ax=None):
        fig, ax = plt.subplots()
        img = self.image_load(name=name)
        ax.imshow(img, cmap=use_cmap, vmin=0, vmax=255)
        ax.set_title("" + self.image_name(name=name) + " in year: " + str(self.image_year(name=name)))
        return fig
#lat_regression is a linear regression function of latitude on land usage code    
    def lat_regression(self, use_code=None, ax=None):
        lr = LinearRegression()
        df = self.df[self.df["name"].str.match("samp")]
        df = df[df["name"] != "madison"]

        header = ["year", "image", "name", "lat", "lon", "percent"]
        df["percent"] = None
        lst = []
        for index, row in df.iterrows():
            a = self.image_load(df.iloc[index-60][header.index("image")])
            lst.append((a == use_code).astype(int).mean() * 100)
        df["percent"] = lst 
        lr.fit(df[["lat"]], df[["percent"]])
        slope = lr.coef_[0]
        intercept = lr.intercept_
        
        if ax == None:
            return (slope[0], intercept[0])
        else:
            ax.scatter(x=df["lat"], y = df["percent"])
            ax.set_xlim(42.4)
            ax.set_ylim(0)
            x0 = 0
            x1 = 48
            y0 = intercept
            y1 = (x1 * slope) + intercept
            ax.plot((x0, x1), (y0, y1))
            ax.set_xlabel("Latitude")
            ax.set_ylabel("Percent of Use Code")
            plt.show()
            return (slope[0], intercept[0])
#Same as lat_regressions, but only data points with a name are used, the x-axis will be a year instead of latitude, and you can pass a list of codes to use_code        
    def city_regression(self, use_code=[], year=None): 
        lr = LinearRegression()
        df = self.df                
        header = ["year", "image", "name", "lat", "lon", "percent"]
        df["percent"] = None
        lst = []        
        for index, row in df.iterrows():
            a = self.image_load(df.iloc[index][header.index("image")])
            percent_with_code = []
            for code in use_code:
                percent_with_code.append((a == code).astype(int).mean() * 100)
            total_percent = sum(percent_with_code)
            lst.append(total_percent)
        df["percent"] = lst 
        d = {}
        cities = ["madison", "milwaukee", "greenbay", "kenosha", "racine", "appleton",
                  "waukesha", "oshkosh", "eauclaire", "janesville"]   
        
        for city in cities:
            city_df = df[df["name"] == city]
            lr.fit(city_df[["year"]], city_df[["percent"]])
            slope = lr.coef_[0]
            intercept = lr.intercept_
            projection = (slope*year) + intercept 
            d[city] = projection[0] 

#https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
#getting key from highest value 
        highest = max(d.keys(), key=(lambda key: d[key]))
        return (highest, d[highest])
#For a give city, city_plot will return a chart showing the total percentage of all land use codes for every year 
    def city_plot(self, name):
        d = {}
        header = ["year", "image", "name", "lat", "lon"]
        df = self.df
        city_df = df[df["name"] == name]
        years = []
        for code in use_codes:
            d[code] = []
            for i in range(len(city_df)):
                years.append(city_df.iloc[i][header.index("year")])
                a = self.image_load(city_df.iloc[i][header.index("image")])
                yearly = (a == code).astype(int).mean() * 100  
                if int(code) in a:
                    d[code].append(yearly)
        fig, ax = plt.subplots()        
        for key, value in d.items():
            if len(value) != 0:
                ax.plot(range(0, len(value)), value, label = use_codes[key])
        
        ax.set_title(name)
        plt.legend()
        ax.set_ylabel("Percent")
        ax.set_xticks([0,1,2,3,4,5,6])
        ax.set_xticklabels(["2001", "2004", "2006", "2008", "2011", "2013", "2016"])
        plt.legend(bbox_to_anchor=(1, 2), loc='upper left', ncol=1)     
        plt.show()                   
        return ax
#https://stackoverflow.com/questions/22417323/how-do-enter-and-exit-work-in-python-decorator-classes 
#Kept getting warnings on creating the df 
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False 
        self.db.close()
        return True

    def close(self):
        return self.db.close()
    

    
    
    
    
    
    
    