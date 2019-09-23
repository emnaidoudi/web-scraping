import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
import numpy as np
from sklearn.utils import shuffle
from time import sleep
from selenium.webdriver.common.keys import Keys

def afficher_tous(current_driver):
    button=current_driver.find_element_by_link_text("AFFICHER TOUS LES ARTICLES")
    button.click()
    sleep(7)
    elm=current_driver.find_element_by_tag_name("html")
    elm.send_keys(Keys.END)
    sleep(5)
    elm.send_keys(Keys.HOME)
    page_source = current_driver.page_source    
    current_soup=BeautifulSoup(page_source,'html5lib')
    return current_soup


def get_driver(url):
    driver = webdriver.Chrome('./chromedriver')
    sleep(4) 
    driver.get(url)
    sleep(4)
    return driver

driver_cigarette=get_driver("https://www.evaps.fr/boutique.html")

soup=afficher_tous(driver_cigarette)

def detail_page(soup):  
    all_devs=links=soup.select('div[class="infos-box"]')
    all_links=[l.select_one('a') for l in all_devs]
    hrefs=["https://www.evaps.fr/"+l.get("href") for l in all_links]
    return hrefs

def go_categorie_xpath(xpath):
    href=driver_cigarette.find_element_by_xpath(xpath).get_attribute("href")
    cat_driver=get_driver(href)
    cat_soup=afficher_tous(cat_driver)
    return cat_soup  


def fill_features(which_soup):
    all_lab=which_soup.select('div[class="infos-box"]')
    labs=[n.select('a[class="libelle"]') for n in all_lab ]
    all_names=[n[0].get_text() for n in labs]  
    list_brand=[b.split("-",1)[1] if b.find("-")!=-1 else np.nan for b in all_names]
    return {"Names":all_names, "Brands":list_brand}      


def list_deatil(soup):
    hrefs=detail_page(soup)
    liste_prix=list()
    liste_imgs=list()
    liste_desc=list()
    def list_prix():
        for h in hrefs:
            print("href : "+h)
            p=requests.get(h)
            soup_alterna=BeautifulSoup(p.text,'html5lib')
            prix=soup_alterna.select('span[itemprop="price"]')[0].get_text()   
            liste_prix.append(prix)
            a=h.split("details-produit.",1)[1]
            b="https://www.evaps.fr/documents/media/images/contenu/"+a
            c=b.replace("html","jpg")
            liste_imgs.append(c)    
            try:
                desc=soup_alterna.select_one("div[id='mini-description'] p").get_text()
            except:
                desc=np.nan
            liste_desc.append(desc)
                    
    list_prix()
    return {"list_prix":liste_prix,"Photo":liste_imgs,"Desc":liste_desc}   
    

def work():
    list_brand=list()
    soup_diy=go_categorie_xpath('//*[@id="menu12"]/a')
    soup_elquide=go_categorie_xpath("//*[@id='menu2']/a")
        
    all_prix_ecigarette=list_deatil(soup)['list_prix']
     
    all_prix_eliquide=list_deatil(soup_elquide)['list_prix']
    all_prix_diy=list_deatil(soup_diy)['list_prix']
    
    all_photo_ecigarette=list_deatil(soup)["Photo"]
    all_photo_eliquide=list_deatil(soup_elquide)["Photo"]
    all_photo_diy=list_deatil(soup_diy)["Photo"]

    all_d_ecigarette=list_deatil(soup)["Desc"]
    all_d_eliquide=list_deatil(soup_elquide)["Desc"]
    all_d_diy=list_deatil(soup_diy)["Desc"]

    names_e_cigarette=fill_features(soup)["Names"]
    names_e_liquide=fill_features(soup_elquide)["Names"]
    names_diy=fill_features(soup_diy)["Names"]

    marque_e_cigarette=fill_features(soup)["Brands"]
    marque_e_liquide=fill_features(soup_elquide)["Brands"]
    marque_e_diy=fill_features(soup_diy)["Brands"]

    categorie_cigarette=["e_cigarette"]*len(names_e_cigarette)
    categorie_liquide=["e_liquide"]*len(names_e_liquide)
    categorie_diy=["diy"]*len(names_diy)
    
    
    Names=names_e_cigarette+names_e_liquide+names_diy
    Brands=marque_e_cigarette+marque_e_liquide+marque_e_diy
    Prices=all_prix_ecigarette+all_prix_eliquide+all_prix_diy
    Categories=categorie_cigarette+categorie_liquide+categorie_diy
    Photos=all_photo_ecigarette+all_photo_eliquide+all_photo_diy
    Descrs=all_d_ecigarette+all_d_eliquide+all_d_diy
    
    df=pd.DataFrame(
    {
        "Name":Names,
        "Price":Prices,
        "Brand":Brands,
        "Categorie":Categories,
        "Photo":Photos,
        "Description":Descrs
       
    },
)
    return  shuffle(df) 
    driver_cigarette.close() 



df=work()

df["Photo"].isnull().all()

df.to_csv("csv_data.csv")


df.to_json("json_data.json")


df.head()

get_ipython().system(' ipython nbconvert --to script .ipynb')

