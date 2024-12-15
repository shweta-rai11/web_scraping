from Bio import Entrez
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
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
    Entrez.email = "swetaraibms@example.com" 
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

def save_accessions_to_sheet(accessions, directory='/Users/swetarai/Downloads', filename="geo_accessions_breast_tumor.xlsx"):
    file_path = os.path.join(directory, filename)
    df = pd.DataFrame(accessions, columns=["GEO Accession Number"])
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")
   
    
keyword = "clinical trial breast tumor "
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

file_path = '/Users/swetarai/Downloads/geo_accessions_breast_tumor.xlsx'
df = pd.read_excel(file_path)
geo_accessions = df['GEO Accession Number'].tolist()
geo_metadata = fetch_pubmed_ids_from_geo(geo_accessions)
metadata_df = pd.DataFrame(geo_metadata)
output_file_path = '/Users/swetarai/Downloads/geo_pubmed_metadata_breast_tumor.xlsx'
metadata_df.to_excel(output_file_path, index=False)
print(f"Data saved to {output_file_path}")

def cleaning(file_path='/Users/swetarai/Downloads/geo_pubmed_metadata_breast_tumor.xlsx', output_file_path2='/Users/swetarai/Downloads/updated_geo_pubmed_metadata_breast.xlsx'):
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
35950920, 39542655, 32787886, 38167224, 
35950920, 31444334, 29452344, 35950920, 
38167224, 36749874, 36585452, 31826955, 
38927507, 35950920, 38300710, 38001082, 
36104343, 33980863, 34728791, 39283720, 
34965952, 36627285, 35568265, 36104343, 
32164626, 30979659, 37882661, 35950920, 
29867922, 31657982
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
output_file_path3 = '/Users/swetarai/Downloads/updated_NCT_WITH_trial_reg_SEARCH_breast.xlsx'
df.to_excel(output_file_path3, index=False)
print(f"Data saved to {output_file_path3}")