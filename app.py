from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('div', attrs={'class':'lister-list'}) 
    
    temp = [] #initiating a tuple

    for i in range(0, 7):
        row = table.find_all('div', class_='lister-item mode-advanced')[i]
    
        #get judul
        judul = row.find_all('a')[1].text
    
        #get IMDb rating then convert it to float datatype
        IMDb = row.find_all('strong')[0].text
        IMDb = float(IMDb)
    
        #get Metascore then convert to int datatype, jika tidak ada metascore nya, maka kita assign dengan 0
        type = 'kosong'
        meta = 0
        if row.find('span', class_='metascore favorable') != None:
            meta = int(row.find('span', class_='metascore favorable').text.strip())
            type = 'favorable'
        elif row.find('span', class_='metascore mixed') != None:
            meta = int(row.find('span', class_='metascore mixed').text.strip())
            type = 'mixed'
        elif row.find('span', class_='metascore unfavorable') != None:
            meta = int(row.find('span', class_='metascore mixed').text.strip())
            type = 'unfavorable'
        
        #get Votes then convert to int
        votes = row.find_all('span', attrs={"name": "nv"})[0].text
        votes = int(votes.replace(',',''))
    
        temp.append((judul, IMDb, meta, type, votes)) 

    df = pd.DataFrame(temp, columns = ('Judul','IMDb', 'metascore', 'type_metascore', 'Votes')) #creating the dataframe
    #data wranggling -  try to change the data type to right data type
    df['type_metascore'] = df['type_metascore'].astype('category')
    #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31&sort=num_votes,desc&view=advanced') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(6,6),dpi=500)
    df[::-1].plot(x='Judul', y='Votes', kind='barh')
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
