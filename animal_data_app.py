import streamlit as st
import pandas as pd
import base64
import numpy as np 
import seaborn as sns
from requests import get
from bs4 import BeautifulSoup as bs
import sqlite3
import matplotlib.pyplot as plt
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp 
            {{ background-image: url("data:image/jpeg;base64,{encoded_string}"); }}
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5);  /* voile noir à 50% */
            z-index: -1;
        }}
        [data-testid="stHeader"], .stApp > header {{ background: rgba(0,0,0,0); }}
        .stApp {{ background-size: cover; background-position: center; background-attachment: fixed; }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local('images/img_file3.jpg')
st.set_page_config(page_title="CoinAfrique Animals Scraper", layout="wide")
st.markdown("""
<style>
    /* Fond général clair */
    .stApp {
        background-color: noir;
    }
    /* Texte principal en blanc (très lisible) */
    .css-1v0mbdj, p, div, span, li {
        color: blanc !important;
    }
    /* Liens en bleu CoinAfrique mais lisibles */
    a {
        color: noir !important;
        font-weight: 600;
    }
    a:hover {
        color: blanc !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>MY DATA APP</h1>", unsafe_allow_html=True)
#st.markdown("<h1 style='text-align: center; color: #2E7D32;'> CoinAfrique Animals Data Scraper </h1>", unsafe_allow_html=True)

st.markdown(""" This application allows scraping animal data from CoinAfrique across multiple pages.And you can also download data already scraped through Web Scraper (uncleaned).
view a dashboard of data (cleaned)
fill in an app evaluation form. 
* **Python Libraries:** pandas, streamlit, requests, bs4, sqlite3, numpy, base64
* **Data Source:** [CoinAfrique Senegal](https://sn.coinafrique.com/)
* **Categories:** Chiens, Moutons, Poules/Lapins/Pigeons, Autres animaux
""")


st.markdown("""
       <style>
               div.stButton {text-align: center;}
       </style>
""", unsafe_allow_html=True)

def init_database():
    conn = sqlite3.connect('coinafrique_animaux.db')
    cursor = conn.cursor()
    
    # Table pour les chiens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chiens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table pour les moutons
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moutons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table pour poules/lapins/pigeons
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poules_lapins_pigeons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            details TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table pour autres animaux
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autres_animaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Fonction pour sauvegarder dans la base de données
def save_to_database(dataframe, table_name):
    conn = sqlite3.connect('coinafrique_animaux.db')
    dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

# Fonction pour charger depuis la base de données
def load_from_database(table_name):
    conn = sqlite3.connect('coinafrique_animaux.db')
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# Fonction de conversion CSV
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Fonction pour afficher et télécharger les données
def load(dataframe, title, key, key1) :
    # Créer 3 colonnes avec celle du milieu plus large
    col1, col2, col3 = st.columns([1, 2, 1])
    
    
    with col2:
        if st.button(f"Afficher {title}", key=f"btn_{key}"):
            st.subheader(f'Dimensions des données - {title}')
            st.write(f'Dimensions: {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes')
            st.dataframe(dataframe, use_container_width=True)
            
            csv = convert_df(dataframe)
            st.download_button(
                label="Télécharger en CSV",
                data=csv,
                file_name=f'{title.replace(" ", "_")}.csv',
                mime='text/csv',
                key=f"download_{key}"
            )

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Fonction de scraping pour les chiens

def  load_scrape_chiens(n_pages):
    df = pd.DataFrame()
    # loop over pages indexes
    for index in range(1, n_pages + 1 ):
        url_1 = f'https://sn.coinafrique.com/categorie/chiens?page={index}'
        # get the code html of the page using the get function requests
        res = get(url_1)
        # stock the html in a beautifulsoup objet with a html parser (a parser allows to easily navigate through the html code)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', 'col s6 m4 l3')
        data = []
        for container in containers:
            try:
                #scrape the following informations: 
                Name=container.find('p', 'ad__card-description').a.text
                #get price
                price="".join(container.find('p', 'ad__card-price').text.strip().split()).replace('CFA', '')
                #get adress
                adress= "".join(container.find('p', 'ad__card-location').text.strip().split()).replace("location_on","")
                # get image_link
                img = container.find('img')
                img_link = img['src']
                dic={
                    "Name":Name,
                    "price":price,
                    "adress":adress,
                    "img_link":img_link
                }
                data.append(dic)

            except:
                pass
        DF=pd.DataFrame(data)
        df=pd.concat([df,DF],axis=0).reset_index(drop=True)
    return df

# Fonction de scraping pour les moutons
def  load_scrape_moutons(n_pages):
    df = pd.DataFrame()
    # loop over pages indexes
    for index in range(1, n_pages + 1 ):
        url_1 = f'https://sn.coinafrique.com/categorie/moutons?page={index}'
        # get the code html of the page using the get function requests
        res = get(url_1)
        # stock the html in a beautifulsoup objet with a html parser (a parser allows to easily navigate through the html code)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', 'col s6 m4 l3')
        data = []
        for container in containers:
            try:
                #scrape the following informations: 
                Name=container.find('p', 'ad__card-description').a.text
                #get price
                price="".join(container.find('p', 'ad__card-price').text.strip().split()).replace('CFA', '')
                #get adress
                adress= "".join(container.find('p', 'ad__card-location').text.strip().split()).replace("location_on","")
                # get image_link
                img = container.find('img')
                img_link = img['src']
                dic={
                    "Name":Name,
                    "price":price,
                    "adress":adress,
                    "img_link":img_link
                }
                data.append(dic)

            except:
                pass
        DF=pd.DataFrame(data)
        df=pd.concat([df,DF],axis=0).reset_index(drop=True)
    return df


# Fonction de scraping pour poules/lapins/pigeons
def  load_scrape_poules_lapins_et_pigeons(n_pages):
    df = pd.DataFrame()
    # loop over pages indexes
    for index in range(1, n_pages + 1 ):
        url_1 = f'https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons?page={index}'
        # get the code html of the page using the get function requests
        res = get(url_1)
        # stock the html in a beautifulsoup objet with a html parser (a parser allows to easily navigate through the html code)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', 'col s6 m4 l3')
        data = []
        for container in containers:
            try:
                #scrape the following informations: 
                Name=container.find('p', 'ad__card-description').a.text
                #get price
                price="".join(container.find('p', 'ad__card-price').text.strip().split()).replace('CFA', '')
                #get adress
                adress= "".join(container.find('p', 'ad__card-location').text.strip().split()).replace("location_on","")
                # get image_link
                img = container.find('img')
                img_link = img['src']
                dic={
                    "Name":Name,
                    "price":price,
                    "adress":adress,
                    "img_link":img_link
                }
                data.append(dic)

            except:
                pass
        DF=pd.DataFrame(data)
        df=pd.concat([df,DF],axis=0).reset_index(drop=True)
    return df

# Fonction de scraping pour autres animaux
def  load_scrape_autres_animaux(n_pages):
    df = pd.DataFrame()
    # loop over pages indexes
    for index in range(1, n_pages + 1 ):
        url_1 = f'https://sn.coinafrique.com/categorie/autres-animaux?page={index}'
        # get the code html of the page using the get function requests
        res = get(url_1)
        # stock the html in a beautifulsoup objet with a html parser (a parser allows to easily navigate through the html code)
        soup = bs(res.content, 'html.parser')
        containers = soup.find_all('div', 'col s6 m4 l3')
        data = []
        for container in containers:
            try:
                #scrape the following informations: 
                Name=container.find('p', 'ad__card-description').a.text
                #get price
                price="".join(container.find('p', 'ad__card-price').text.strip().split()).replace('CFA', '')
                #get adress
                adress= "".join(container.find('p', 'ad__card-location').text.strip().split()).replace("location_on","")
                # get image_link
                img = container.find('img')
                img_link = img['src']
                dic={
                    "Name":Name,
                    "price":price,
                    "adress":adress,
                    "img_link":img_link
                }
                data.append(dic)

            except:
                pass
        DF=pd.DataFrame(data)
        df=pd.concat([df,DF],axis=0).reset_index(drop=True)
    return df

# Interface utilisateur
st.sidebar.header('Paramètres')
pages = st.sidebar.selectbox('Nombre de pages à scraper', list(range(1, 17)))
category = st.sidebar.selectbox('Catégorie', ['Toutes', 'Chiens', 'Moutons', 'Poules/Lapins/Pigeons', 'Autres animaux'])
choice = st.sidebar.selectbox('Options', [
    'Scraper les données',
    'Télécharger données scrapées',
    'Dashboard des données',
    'Évaluer l\'application'
])

# Initialiser la base de données
init_database()
#add_bg_from_local('img_file3.jpg') 

#local_css('style.css')  
if choice == 'Scraper les données':
    st.header("Scraping des données")
    
    if st.button(" Lancer le scraping", type="primary"):
        categories_to_scrape = []
        
        if category == 'Toutes':
            categories_to_scrape = ['Chiens', 'Moutons', 'Poules/Lapins/Pigeons', 'Autres animaux']
        else:
            categories_to_scrape = [category]
        
        for cat in categories_to_scrape:
            st.subheader(f" Scraping: {cat}")
            
            if cat == 'Chiens':
                df =load_scrape_chiens(pages)
                if not df.empty:
                    save_to_database(df, 'chiens')
                    st.success(f"{len(df)} chiens scrapés avec succès!")
                    st.dataframe(df)
                    
                    # Bouton de téléchargement
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Télécharger Chiens CSV",
                        data=csv,
                        file_name='chiens.csv',
                        mime='text/csv',
                        key='download_chiens_scraped'
                    )
                    
            elif cat == 'Moutons':
                df = load_scrape_moutons(pages)
                if not df.empty:
                    save_to_database(df, 'moutons')
                    st.success(f"{len(df)} moutons scrapés avec succès!")
                    st.dataframe(df)
                    
                    # Bouton de téléchargement
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Télécharger Chiens CSV",
                        data=csv,
                        file_name='moutons',
                        mime='text/csv',
                        key='download_moutons_scraped'
                    )
                    
            elif cat == 'Poules/Lapins/Pigeons':
                df = load_scrape_poules_lapins_et_pigeons(pages)
                if not df.empty:
                    save_to_database(df, 'poules_lapins_pigeons')
                    st.success(f"{len(df)} chiens scrapés avec succès!")
                    st.dataframe(df)
                    
                    # Bouton de téléchargement
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Télécharger poules_lapins_pigeons CSV",
                        data=csv,
                        file_name='poules_lapins_pigeons.csv',
                        mime='text/csv',
                        key='download_poules_lapins_pigeons_scraped'
                    )
            elif cat == 'Autres animaux':
                df = load_scrape_autres_animaux(pages)
                if not df.empty:
                    save_to_database(df, 'autres_animaux')
                    st.success(f"{len(df)} chiens scrapés avec succès!")
                    st.dataframe(df)
                    
                    # Bouton de téléchargement
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Télécharger autres_animaux CSV",
                        data=csv,
                        file_name='autres_animaux.csv',
                        mime='text/csv',
                        key='download_autres_animaux_scraped'
                    )

elif choice == 'Télécharger données scrapées':
    st.header("Télécharger les données de la base")
    
    chiens = pd.read_csv('data/categories_chiens_sitemap.csv')
    poules_lapins_pigeons = pd.read_csv('data/categorie_poules_lapins_et_pigeons.csv')
    moutons = pd.read_csv('data/categorie_moutons.csv')
    autres_animaux = pd.read_csv('data/categorie_autres_animaux.csv')
    # load the data
    load( chiens, 'chiens', '1', '101')
    load(poules_lapins_pigeons, 'poules lapins pigeons', '2', '102')
    load(moutons , 'moutons', '3', '103')
    load(autres_animaux, 'autres animaux', '4', '104')

elif choice == 'Dashboard des données':
    st.header("Tableau de bord")
    
    try:
        # Charger toutes les données
        df_chiens = load_from_database('chiens')
        df_moutons = load_from_database('moutons')
        df_plp = load_from_database('poules_lapins_pigeons')
        df_autres = load_from_database('autres_animaux')
        
        # Statistiques générales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" Chiens", len(df_chiens))
        with col2:
            st.metric("Moutons", len(df_moutons))
        with col3:
            st.metric(" Poules/Lapins/Pigeons", len(df_plp))
        with col4:
            st.metric(" Autres animaux", len(df_autres))
        
        # Graphiques
        st.subheader("Distribution par catégorie")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ['Chiens', 'Moutons', 'Poules/Lapins/Pigeons', 'Autres']
        counts = [len(df_chiens), len(df_moutons), len(df_plp), len(df_autres)]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        ax.bar(categories, counts, color=colors)
        ax.set_xlabel('Catégories')
        ax.set_ylabel('Nombre d\'annonces')
        ax.set_title('Distribution des annonces par catégorie')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Top addresses
        st.subheader("Top localisations")
        
        all_adress = pd.concat([
            df_chiens[['adress']] if not df_chiens.empty else pd.DataFrame(),
            df_moutons[['adress']] if not df_moutons.empty else pd.DataFrame(),
            df_autres[['adress']] if not df_autres.empty else pd.DataFrame()
        ])
        
        if not all_adress.empty:
            top_adress = all_adress['adress'].value_counts().head(10)
            
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.barh(top_adress.index, top_adress.values, color='#95E1D3')
            ax2.set_xlabel('Nombre d\'annonces')
            ax2.set_title('Top 10 des localisations')
            st.pyplot(fig2)
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.info("Veuillez d'abord scraper des données ou vérifier que la base de données contient des informations.")

else:  # Évaluer l'application
    st.header(" Évaluation de l'application")
    st.markdown("<h3 style='text-align: center;'>Donnez votre avis</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Formulaire Kobo"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://ee.kobotoolbox.org/x/fWIhpUbp">',
                unsafe_allow_html=True
            )
    
    with col2:
        if st.button(" Formulaire Google"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://docs.google.com/forms/d/e/1FAIpQLSfGUlpFy6i2tuhoCFu00O4dQRSef_60YG_GXljsi7ski4VFmw/viewform?usp=header">',
                unsafe_allow_html=True
            )



