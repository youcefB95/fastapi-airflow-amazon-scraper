from typing import List
from fastapi import FastAPI
from datetime import date
from pydantic import BaseModel
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re 
import time
import pandas as pd
from bs4 import BeautifulSoup

app = FastAPI()

# Scraper pour récupérer les données d'Amazon (comme dans ton exemple)

def get_amazon_data_books(num_books):
    hub_url = "http://selenium-hub:4444/wd/hub"

    print("cool")
    chrome_options = Options()
    chrome_options.add_argument("--headless") 

    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36"
    )


    driver = webdriver.Remote(command_executor=hub_url, options=chrome_options)
    print("step1")

    driver.set_page_load_timeout(30) 
    # URL de base pour la recherche de livres
    
    base_url = "https://www.amazon.com/s?k=data+engineering+books"

    books = []
    seen_titles = set()  # Pour garder la trace des titres déjà vus

    page = 1

    while len(books) < num_books:
        url = f"{base_url}&page={page}"
        
        # Ouvrir la page dans le navigateur via Selenium
        driver.get(url)
        print("step2")
        

        # Attendre que l'élément de résultats soit présent
        #wait = WebDriverWait(driver, 10)
        #wait.until(EC.presence_of_element_located((By.ID, "search")))
        
    
         # Ajustez le temps d'attente selon la vitesse de votre connexion

        # Récupérer le code source de la page après chargement complet
        page_source = driver.page_source

        # Analyser le code source avec BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Trouver les éléments contenant les livres (ajustez le sélecteur selon la structure HTML réelle)
        book_containers = soup.find_all("div", class_=re.compile(".*s-result-item.*"))
        print("step3")

        # Extraire les informations sur les livres
        for book in book_containers:
            try:
                title_element = book.find('h2', class_=re.compile(".*a-size-base-plus.*"))
                author_element = book.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')
                price_whole = book.find('span', class_='a-price-whole')
                price_decimal = book.find('span', class_='a-price-fraction')  # Correction pour le prix fractionnaire
                rating_span = book.find('span', class_='a-icon-alt')
                img_element = book.find('img', class_='s-image')
                
                # Vérifier que tous les éléments existent
                if title_element and author_element and price_whole and price_decimal and rating_span:
                    book_title = title_element.get_text(strip=True)
                    print(book_title)
                    
                    # Vérifier si le titre a déjà été vu
                    if book_title not in seen_titles:
                        seen_titles.add(book_title)
                        books.append({
                            "Title": book_title,
                            "Author": author_element.get_text(strip=True),
                            "Price": price_whole.get_text(strip=True) + "." + price_decimal.get_text(strip=True),
                            "Rating": rating_span.get_text(strip=True),
                            "Image": img_element["src"] if img_element else "" ,
                            "Date" : date.today()
                        })
            except Exception as e:
                print(f"Erreur lors du traitement d'un livre : {e}")
        
        # Passer à la page suivante
        page += 1

        # Si aucune nouvelle donnée n'est collectée, arrêter pour éviter une boucle infinie
        if len(books) == len(seen_titles):
            print("Aucune nouvelle donnée collectée, arrêt.")
            break

    # Limiter à la quantité demandée de livres
    books = books[:num_books]

    # # Convertir la liste de dictionnaires en DataFrame
    # df = pd.DataFrame(books)

    # # Afficher le DataFrame
    # print(df)
    

    driver.quit()
    
    return books

def fetch_amazon_top_best_selling_books(num_books):
    hub_url = "http://selenium-hub:4444/wd/hub"

    print("cool")
    chrome_options = Options()
    chrome_options.add_argument("--headless") 

    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36"
    )


    driver = webdriver.Remote(command_executor=hub_url, options=chrome_options)
    print("step1")

    driver.set_page_load_timeout(30) 
    # URL de base pour la recherche de livres
    
    base_url = "https://www.amazon.com/s?k=data+engineering+books&s=exact-aware-popularity-rank&qid=1734622043&ref=sr_st_exact-aware-popularity-rank&ds=v1%3AhMN9DdsxLFEU6A4wN2HVGdXJ98Rf4I%2BLLLeurDCfZ4c"

    books = []
    seen_titles = set()  # Pour garder la trace des titres déjà vus

    page = 1

    while len(books) < num_books:
        url = f"{base_url}&page={page}"
        
        # Ouvrir la page dans le navigateur via Selenium
        driver.get(url)
        print("step2")
        

        # Attendre que l'élément de résultats soit présent
        #wait = WebDriverWait(driver, 10)
        #wait.until(EC.presence_of_element_located((By.ID, "search")))
        
    
         # Ajustez le temps d'attente selon la vitesse de votre connexion

        # Récupérer le code source de la page après chargement complet
        page_source = driver.page_source

        # Analyser le code source avec BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Trouver les éléments contenant les livres (ajustez le sélecteur selon la structure HTML réelle)
        book_containers = soup.find_all("div", class_=re.compile(".*s-result-item.*"))
        print("step3")

        # Extraire les informations sur les livres
        for book in book_containers:
            try:
                title_element = book.find('h2', class_=re.compile(".*a-size-base-plus.*"))
                author_element = book.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')
                price_whole = book.find('span', class_='a-price-whole')
                price_decimal = book.find('span', class_='a-price-fraction')  # Correction pour le prix fractionnaire
                rating_span = book.find('span', class_='a-icon-alt')
                img_element = book.find('img', class_='s-image')
                
                # Vérifier que tous les éléments existent
                if title_element and author_element and price_whole and price_decimal and rating_span:
                    book_title = title_element.get_text(strip=True)
                    print(book_title)
                    
                    # Vérifier si le titre a déjà été vu
                    if book_title not in seen_titles:
                        seen_titles.add(book_title)
                        books.append({
                            "Title": book_title,
                            "Author": author_element.get_text(strip=True),
                            "Price": price_whole.get_text(strip=True) + "." + price_decimal.get_text(strip=True),
                            "Rating": rating_span.get_text(strip=True),
                            "Image": img_element["src"] if img_element else "" ,
                            "Date" : date.today()
                        })
            except Exception as e:
                print(f"Erreur lors du traitement d'un livre : {e}")
        
        # Passer à la page suivante
        page += 1

        # Si aucune nouvelle donnée n'est collectée, arrêter pour éviter une boucle infinie
        if len(books) == len(seen_titles):
            print("Aucune nouvelle donnée collectée, arrêt.")
            break

    # Limiter à la quantité demandée de livres
    books = books[:num_books]

    # # Convertir la liste de dictionnaires en DataFrame
    # df = pd.DataFrame(books)

    # # Afficher le DataFrame
    # print(df)
    

    driver.quit()
    
    return books




# Pydantic model pour les livres
class Book(BaseModel):
    Title: str
    Author: str
    Price: str
    Rating: str
    Image: str
    Date : date

@app.get("/get_books", response_model=List[Book])
async def get_books(num_books: int = 10):
    books = get_amazon_data_books(num_books)
    return books



@app.get("/get_top_books", response_model=List[Book])
async def get_top_books(num_books: int = 10):
    books = fetch_amazon_top_best_selling_books(num_books)
    return books
