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
            background: rgba(0, 0, 0, 0.5);  /* voile noir  */
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
    /* Fond crème/beige clair pour la page principale */
    .stApp {
        background-color: #FFF8E7 !important;
    }
    
    /* Sidebar en orange CoinAfrique vibrant */
    [data-testid="stSidebar"] {
        background-color: #FF6B35 !important;
    }
    
    /* Texte blanc dans le sidebar pour les labels */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Les selectbox et inputs en BLANC dans le sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Dropdown menu en BLANC */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Menu déroulant ouvert en BLANC */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    
    [data-baseweb="popover"] * {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Liste déroulante en blanc avec texte noir */
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
    }
    
    ul[role="listbox"] li {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Au survol: fond blanc et texte noir */
    ul[role="listbox"] li:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Boutons de téléchargement en BLANC dans le sidebar */
    [data-testid="stSidebar"] .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background-color: #F0F0F0 !important;
        color: #000000 !important;
    }
    
    /* Texte marron foncé sur la page principale */
    .stApp * {
        color: #3E2723 !important;
    }
    
    p, div, span, li, h1, h2, h3, h4, h5, h6, 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stText"] {
        color: #3E2723 !important;
    }
    
    /* Titres en marron très foncé */
    h1, h2, h3, h4, h5, h6 {
        color: #2C1810 !important;
        font-weight: 800 !important;
    }
    
    /* Liens en orange vif */
    a {
        color: #FF6B35 !important;
        font-weight: 700;
    }
    a:hover {
        color: #FF8C42 !important;    
    }
    
    /* Boutons normaux en orange harmonisé */
    .stButton > button {
        background-color: #FF6B35 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>ANIMAL DATA APP</h1>", unsafe_allow_html=True)
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
    
    # Table for dogs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chiens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table for the sheep
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moutons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table for chickens/rabbits/pigeons
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poules_lapins_pigeons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            details TEXT,
            price TEXT,
            adress TEXT,
            img_link TEXT
        )
    ''')
    
    # Table for other animals
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

def save_to_database(dataframe, table_name):
    conn = sqlite3.connect('coinafrique_animaux.db')
    dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def load_from_database(table_name):
    conn = sqlite3.connect('coinafrique_animaux.db')
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

def load(dataframe, title, key, key1) :
    # Créer 3 colonnes avec celle du milieu plus large
    col1, col2, col3 = st.columns([1, 2, 1])
    
    
    with col2:
        if st.button(f"Afficher {title}", key=f"btn_{key}"):
            st.subheader(f'Data Dimensions - {title}')
            st.write(f'Dimensions: {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes')
            st.dataframe(dataframe, use_container_width=True)
            
            csv = convert_df(dataframe)
            st.download_button(
                label="Download as CSV",
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

# Scraping function for sheep
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


# Scraping function for chickens/rabbits/pigeons
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

# Scraping function for other animals
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

# User interface
st.sidebar.header('Settings')
pages = st.sidebar.selectbox('Number of pages to scrape', list(range(1, 17)))
category = st.sidebar.selectbox('Category', ['All', 'Dogs', 'Sheep', 'Chickens/Rabbits/Pigeons', 'Other animals'])
choice = st.sidebar.selectbox('Options', [
    'scrape data across multiple pages',
    'Download data with web scraper',
    'Data Dashboard',
    'Evaluate the application'
])

# Initialize the database
init_database()
 
if choice == 'scrape data across multiple pages':
    st.header("Data scraping")
    
    if st.button(" Start scraping", type="primary"):
        categories_to_scrape = []
        
        if category == 'All':
            categories_to_scrape = ['Dogs', 'Sheep', 'Chickens/Rabbits/Pigeons', 'Other animals']
        else:
            categories_to_scrape = [category]
        
        for cat in categories_to_scrape:
            st.subheader(f" Scraping: {cat}")
            
            if cat == 'Dogs':
                df =load_scrape_chiens(pages)
                if not df.empty:
                    save_to_database(df, 'chiens')
                    st.success(f"{len(df)} Dogs successfully scrapped!")
                    st.dataframe(df)
                    
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Download Dogs CSV",
                        data=csv,
                        file_name='chiens.csv',
                        mime='text/csv',
                        key='download_chiens_scraped'
                    )
                    
            elif cat == 'Sheep':
                df = load_scrape_moutons(pages)
                if not df.empty:
                    save_to_database(df, 'moutons')
                    st.success(f"{len(df)} Sheep successfully scrapped!")
                    st.dataframe(df)
                    
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Download sheep CSV",
                        data=csv,
                        file_name='moutons',
                        mime='text/csv',
                        key='download_moutons_scraped'
                    )
                    
            elif cat == 'Chickens/Rabbits/Pigeons':
                df = load_scrape_poules_lapins_et_pigeons(pages)
                if not df.empty:
                    save_to_database(df, 'poules_lapins_pigeons')
                    st.success(f"{len(df)} Chickens/Rabbits/Pigeons successfully scrapped!")
                    st.dataframe(df)
                    
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Download chickens_rabbits_pigeons CSV",
                        data=csv,
                        file_name='poules_lapins_pigeons.csv',
                        mime='text/csv',
                        key='download_poules_lapins_pigeons_scraped'
                    )
            elif cat == 'Other animals':
                df = load_scrape_autres_animaux(pages)
                if not df.empty:
                    save_to_database(df, 'autres_animaux')
                    st.success(f"{len(df)} Other animals successfully scrapped!")
                    st.dataframe(df)
                    
                    csv = convert_df(df)
                    st.download_button(
                        label="⬇Download other_animals CSV",
                        data=csv,
                        file_name='autres_animaux.csv',
                        mime='text/csv',
                        key='download_autres_animaux_scraped'
                    )
elif choice == 'Download data with web scraper':
    st.header("download the database data")
    
    chiens = pd.read_csv('data/categories_chiens_sitemap.csv')
    poules_lapins_pigeons = pd.read_csv('data/categorie_poules_lapins_et_pigeons.csv')
    moutons = pd.read_csv('data/categorie_moutons.csv')
    autres_animaux = pd.read_csv('data/categorie_autres_animaux.csv')
    # load the data
    load( chiens, 'chiens', '1', '101')
    load(poules_lapins_pigeons, 'poules lapins pigeons', '2', '102')
    load(moutons , 'moutons', '3', '103')
    load(autres_animaux, 'autres animaux', '4', '104')
elif choice == 'Data Dashboard':
    st.divider()
    st.header("Tableau de bord")
    
    try:
        df_chiens = load_from_database('chiens')
        df_moutons = load_from_database('moutons')
        df_plp = load_from_database('poules_lapins_pigeons')
        df_autres = load_from_database('autres_animaux')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" Dogs", len(df_chiens))
        with col2:
            st.metric("Sheep", len(df_moutons))
        with col3:
            st.metric(" Chickens/Rabbits/Pigeons", len(df_plp))
        with col4:
            st.metric(" Other animals", len(df_autres))
        
        # Graphiques
        st.subheader("Distribution by category")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ['Chiens', 'Moutons', 'Poules/Lapins/Pigeons', 'Autres']
        counts = [len(df_chiens), len(df_moutons), len(df_plp), len(df_autres)]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        ax.bar(categories, counts, color=colors)
        ax.set_xlabel('Categories')
        ax.set_ylabel('Number of ads')
        ax.set_title('Distribution of ads by category')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        # Top addresses
        st.subheader("Top locations")
        
        all_adress = pd.concat([
            df_chiens[['adress']] if not df_chiens.empty else pd.DataFrame(),
            df_moutons[['adress']] if not df_moutons.empty else pd.DataFrame(),
            df_plp[['adress']] if not df_plp.empty else pd.DataFrame(),
            df_autres[['adress']] if not df_autres.empty else pd.DataFrame()
        ])
        
        if not all_adress.empty:
            top_adress = all_adress['adress'].value_counts().head(10)
            
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.barh(top_adress.index, top_adress.values, color='#95E1D3')
            ax2.set_xlabel('Number of ads')
            ax2.set_title('Top 10 locations')
            st.pyplot(fig2)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Dashboard data not available yet.")

else:  
    st.header(" Evaluate the application")
    st.markdown("<h3 style='text-align: center;'>Give your opinion</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Kobo Form"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://ee.kobotoolbox.org/x/fWIhpUbp">',
                unsafe_allow_html=True
            )
    
    with col2:
        if st.button(" Google Form"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://docs.google.com/forms/d/e/1FAIpQLSfGUlpFy6i2tuhoCFu00O4dQRSef_60YG_GXljsi7ski4VFmw/viewform?usp=header">',
                unsafe_allow_html=True
            )



