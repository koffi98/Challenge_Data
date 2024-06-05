import csv
import time
from datetime import date
from pathlib import Path
import unidecode
import pandas
from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup





class PostModelInterface(object):
    """
    schema correspondant aux poste linkedin pour la validation des champs
    """
    author: str
    content: str
    author_descrition: str
    reactions: int
    comments: str | None
    comments_number: int | None
    tags: list[str] | None

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "content": self.content,
            "author_descrition": self.author_descrition,
            "reactions": self.reactions,
            "comments": self.comments,
            "tags": self.tags,
        }

    @staticmethod
    def get_rows():
        return ['author', 'content', 'author_descrition', 'reactions', 'comments','comments_number', 'tags']


def get_keywork_result(driver: webdriver.Chrome, keyword: str) -> str:
    """
    Extrait le contenu HTLM en fonction des mots clés recherchés
    :param url:
    :param driver:
    :return htlm_content for keywords:
    """
    # recherche du mot cle
    time.sleep(5)
    champ_search = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
    champ_search.clear()
    champ_search.send_keys(keyword)
    champ_search.send_keys(Keys.RETURN)
    time.sleep(7)

    # recuperation du contenu html
    return driver.page_source

def search_linkedin(driver, query):
    search_box = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-global-typeahead__input'))
    )
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    # Filtrer les résultats pour n'afficher que les posts
    posts_button = WebDriverWait(driver, 40).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Posts"]'))
    )
    posts_button.click()

def setup_linkedin_driver(username: str, password: str) -> webdriver.Chrome:
    """
    Configuration de l'agent linkedin
    :param username:
    :param password:
    :return:
    """
    print("start to setup driver")
    # instanciation du driver
    driver = webdriver.Chrome()

    # aller sur linkedin
    driver.get("https://www.linkedin.com/login")

    time.sleep(5)

    # se connecter
    driver.find_element(By.ID, "username").send_keys(username)
    # driver.find_element(By.ID, "password").send_keys(password)
    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys(password)

    # Soumettre le formulaire de connexion
    password_input.send_keys(Keys.RETURN)
    
    # driver.find_element(By.CLASS_NAME, "sign-in-form__submit-btn--full-width").click()
    # driver.send_keys(Keys.RETURN)
    return driver



def result_to_csv(results: list[dict], file: Path):
    """
    Enregistrer les resultats dans un fichier
    :param results:
    :param file:
    """
    df = pandas.DataFrame(results, columns=PostModelInterface.get_rows())
    df.to_csv(str(file), index=False, mode='a')

def contains_cybersecurity_keywords(text, cybersecurity_keywords):
    return any(unidecode.unidecode(keyword.lower()) in unidecode.unidecode(text.lower()) for keyword in cybersecurity_keywords)

def extract_posts(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    posts = []
    
    post_elements = soup.select('div.feed-shared-update-v2')
    
    for post in post_elements:
        post_obj = PostModelInterface()
        try:
            try:
                post_obj.author = post.select_one('span.update-components-actor__name').get_text(strip=True)
            except:
                post_obj.author = None
            try:
                post_obj.author_descrition = post.select_one('span.update-components-actor__description').get_text(strip=True)
            except:
                post_obj.author_descrition = None
            try:
                post_obj.content = post.select_one('div.update-components-text.relative.update-components-update-v2__commentary').get_text(strip=True)
            except:
                post_obj.content = None

            # Extraire le nombre de réactions
            try:
                post_obj.reactions = post.select_one('span.social-details-social-counts__social-proof-fallback-number').get_text(strip=True)
            except Exception:
                post_obj.reactions = None
            
            # Extraire le nombre de commentaires
            try:
                #post_obj.comments = post.select_one('li.social-details-social-counts__comments button span').get_text(strip=True)
                post_obj.comments = post.select_one('button.social-details-social-counts__count-value span[aria-hidden="true"]').get_text(strip=True)
                post_obj.comments_number = post_obj.comments_number.split()[0]
            except Exception:
                post_obj.comments = None
                post_obj.comments_number = None
            
            # Extraire les hashtags
            post_obj.tags=[]
            for tag in post.select('a[href*="hashtag"]'):
                hashtag_text = tag.get_text(strip=True)
                if not hashtag_text.startswith('#'):
                    hashtag_text = f'#{hashtag_text}'
                post_obj.tags.append(hashtag_text.split("#")[-1 ])
            
            
            print(post_obj.to_dict())
            posts.append(post_obj.to_dict())
        
        except Exception as e:
            print(f"Error extracting post info: {e}")

    return posts


# if __name__=="__main__":
#     print("a")
#     username = 
#     password = 
#     try:
#         driver = setup_linkedin_driver(username, password)
#         print("driver ok")
#         posts = scrape_posts(driver)
#         for post in posts:
#             print(post)
#     finally:
#         driver.quit()