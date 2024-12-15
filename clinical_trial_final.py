from Bio import Entrez
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd

def search_geo_accessions(keyword, retmax=2000, retstart=0):
    Entrez.email = "swetaraibms@example.com"  
    search_results = []
    handle = Entrez.esearch(db="gds", term=keyword, retmax=retmax, retstart=retstart)
    record = Entrez.read(handle)
    handle.close()
    id_list = record.get("IdList", [])
    return id_list, int(record.get("Count", 0))

def fetch_geo_accession_details(id_list):
    Entrez.email = "swetaraibms@example.com"  # email
    accession_numbers = set() 
    
    if id_list:
        handle = Entrez.efetch(db="gds", id=id_list, rettype="full", retmode="text")
        data = handle.read()  
        handle.close()
        accession_pattern = re.compile(r"GSE\d{6,7}")
        found_accessions = accession_pattern.findall(data)
        accession_numbers.update(found_accessions)
    else:
        id_list is None

    return list(accession_numbers)  

def fetch_all_geo_accessions(keyword, max_results=2000):
    all_accessions = set()
    retstart = 0
    while True:
        geo_ids, total_count = search_geo_accessions(keyword, retmax=max_results, retstart=retstart)
        if geo_ids is None:
            break
        else:
            accessions = fetch_geo_accession_details(geo_ids)
            all_accessions.update(accessions)
            retstart += max_results
            if retstart >= total_count:
                break
    return list(all_accessions)

def save_accessions_to_sheet(accessions, directory='/Users/swetarai/Downloads', filename="geo_accessions_clinical_trial.xlsx"):
    file_path = os.path.join(directory, filename)
    df = pd.DataFrame(accessions, columns=["GEO Accession Number"])
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")
   
    
keyword = "Clinical trial Cancer "
max_results = 2000 
geo_accessions = fetch_all_geo_accessions(keyword, max_results=max_results)
save_accessions_to_sheet(geo_accessions)


def fetch_pubmed_ids_from_geo(accession_list):
    base_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
    metadata = []

    for accession in accession_list:
        url = f"{base_url}?acc={accession}&view=full"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        pubmed_ids = []
        for a in soup.find_all('a', href=True):
            if 'pubmed' in a['href']:
                pubmed_id = a['href'].split('=')[-1]
                pubmed_ids.append(pubmed_id)

        metadata.append({
            'accession': accession,
            'pubmed_ids': ', '.join(pubmed_ids)  
        })

    return metadata

file_path = '/Users/swetarai/Downloads/geo_accessions_clinical_trial.xlsx'
df = pd.read_excel(file_path)
geo_accessions = df['GEO Accession Number'].tolist()
geo_metadata = fetch_pubmed_ids_from_geo(geo_accessions)
metadata_df = pd.DataFrame(geo_metadata)
output_file_path = '/Users/swetarai/Downloads/geo_pubmed_metadata_clinical_trial.xlsx'
metadata_df.to_excel(output_file_path, index=False)
print(f"Data saved to {output_file_path}")

def cleaning(file_path='/Users/swetarai/Downloads/geo_pubmed_metadata_clinical_trial.xlsx', output_file_path2='/Users/swetarai/Downloads/updated_geo_pubmed_metadata_clinical_trial.xlsx'):
    df = pd.read_excel(file_path)
    df['last_word'] = df['pubmed_ids'].astype(str).apply(lambda x: x.split()[-1])
    df['numerical_id'] = df['last_word'].str.extract('(\d+)$')
    print(df.head())
    df.to_excel(output_file_path2, index=False)
    return df

def fetch_pubmed_html(pubmed_id):
    url = f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def search_nct_in_abstract(html):
    soup = BeautifulSoup(html, 'html.parser')

    abstract_div = soup.find('div', class_='abstract-content selected')
    if abstract_div:
        abstract_text = abstract_div.get_text()

        # Searching for NCT number in the abstract and trial registration sections
        nct_match = re.search(r'NCT\d+', abstract_text)
        if nct_match:
            return nct_match.group(0)
        # Checking if there is a trial registration section
        trial_reg_div = soup.find('div', class_='trial-registration')
        if trial_reg_div:
            trial_reg_text = trial_reg_div.get_text()
            nct_match = re.search(r'NCT\d+', trial_reg_text)
            if nct_match:
                result =nct_match.group(0)
            else:
                result =None
            return result
    else:
        return None

pubmed_ids = [
    34728791, 36922589, 36923308, 36112677, 
    37882661, 37467318, 36165893, 35372008, 
    34675120, 34965952, 33972312, 33495312, 
    31687977, 36104343, 37335139, 33556960, 35357885, 
    38942026, 35022320, 38181044, 34722316, 33951424, 32698374, 38001082, 33303685, 31657982,35388003,
    34644371, 36976323, 31331399, 38401548, 31843922, 37471053, 35950920, 34290408, 38290766, 
    35932450, 34479871, 29490944, 37591207, 26022710, 38238616, 37350957, 38300710, 32661549, 
    38167224, 32668808, 35143711, 29254993, 29716923, 32897363, 35568265, 29571083, 34933343, 
    33980863, 36749874, 34795254, 31826955, 36934257, 32016454, 31300344, 38096050, 29452344, 35058324, 
    36053178, 29867922, 30308012, 34986355, 33916610, 38683966, 34103518, 36505804, 35105718, 37790490, 
    37967116, 36301137, 35138909, 33817986, 36427020, 35354808, 30524706, 35671108, 32358561, 34882581, 
    38862482, 34471863, 34078651, 30742728, 32669548, 36694264, 29229600, 30742122, 35404390, 32164626, 
    38194275, 35681616, 37389981, 38927507, 34322886, 34635775, 33709473, 32812822, 38683200, 35754340, 
    33619369, 31138136, 33893160, 38728872, 33289590, 37966367, 37744358, 34893771, 38373953, 34599153, 
    38626769, 35130560, 36875061, 34256279, 35947123, 37695642, 38630755, 31996669, 33429428, 36849535, 
    37713507, 34224739, 37041632, 31924795, 36928921, 37258531, 31969991, 31709175, 30523719, 33197925, 
    37207208, 31444334, 38167882, 36627285, 36585452, 37938561, 32787886, 32115849, 30108162, 34323958, 
    35349491, 38639919, 38057662, 30979659, 37433032, 37723590, 38345397, 36352190, 
    38655196, 33593877, 38241710, 33911192, 34863853
]
results = []
for pubmed_id in pubmed_ids:
    a = fetch_pubmed_html(pubmed_id)
    if a:
        nct_number = search_nct_in_abstract(a)
        if nct_number:
            results.append({'PubMed ID': pubmed_id, 'NCT Number': nct_number})
        
        else:
            results.append({'PubMed ID': pubmed_id, 'NCT Number': 'NCT Not Found'})
    else:
        results.append({'PubMed ID': pubmed_id,'NCT Number': 'NCT Not Found' })

    
    time.sleep(1)

df = pd.DataFrame(results)
output_file_path3 = '/Users/swetarai/Downloads/updated_NCT_WITH_trial_reg_SEARCH_clinical_trial.xlsx'
df.to_excel(output_file_path3, index=False)
print(f"Data saved to {output_file_path3}")


