import os
from dotenv import load_dotenv
from pathlib import Path
import time
import utils


# charger les variables d'environnements
load_dotenv()

cybersecurity_keywords = [
    "cyber forum Africa", "Cyber Africa Forum"
    'cybersécurité Côte d\'Ivoire', 'cybersecurity Côte d\'Ivoire', 'sécurité informatique Côte d\'Ivoire', 'security Côte d\'Ivoire', 'cyber attack Côte d\'Ivoire',
    'cyber attack Côte d\'Ivoire', 'cyber Côte d\'Ivoire', 'phishing Côte d\'Ivoire', 'malware Côte d\'Ivoire', 'ransomware Côte d\'Ivoire', 'data breach Côte d\'Ivoire', 'firewall Côte d\'Ivoire',
    'cybersécurité Africa', 'cybersecurity Africa', 'sécurité informatique Africa', 'security Africa', 'cyber attack Africa',
    'cyber attack Africa', 'cyber Africa', 'phishing Africa', 'malware Africa', 'ransomware Africa', 'data breach Africa', 'firewall Africa',
    'cybersécurité Afrique', 'cybersecurity Afrique', 'sécurité informatique Afrique', 'security Afrique', 'cyber attack Afrique',
    'cyber attack Afrique', 'cyber Afrique', 'phishing Afrique', 'malware Afrique', 'ransomware Afrique', 'data breach Afrique', 'firewall Afrique', 'cybersécurité en Afrique', 'cybersécurité en Côte d\'Ivoire'
]
max_scroll = 3
keywords_result: list[dict] = []
driver = utils.setup_linkedin_driver(username=os.getenv("LINKEDIN_EMAIL"), password=os.getenv("LINKEDIN_PASSWORD"))

all_posts = []
for query in cybersecurity_keywords:
    utils.search_linkedin(driver, query)
    time.sleep(5)
    scroll_count = 0
    while scroll_count < max_scroll:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        scroll_count += 1
    
    # Récupérer le DOM de la page
    dom = driver.page_source
    
    # Extraire les informations des posts à partir du DOM
    posts = utils.extract_posts(dom)
    if posts:
        utils.result_to_csv(posts, Path('data.csv'))
    all_posts.extend(posts)
    
    # Pause entre les recherches pour éviter d'être bloqué
    time.sleep(5)
driver.quit()
    
