from bs4 import BeautifulSoup
import pandas
import requests
import re

URL = "https://meileaf.com/teas/"

def safepricesearch(obj, key, class_):
    try:
        return(obj.find(key, class_ = class_).text[2:-3])
    except:
        return(100)

def main():
    # Get the HTML from the URL
    html = requests.get(URL).text
    
    # Parse the HTML
    content = BeautifulSoup(html, "html.parser")
    
    # path = "/html/body/main/div[3]/div[1]"
    
    # go to body and main
    main_content = content.find("main")
    
    # go to div with class "container product-index product-index--filterable"
    product_list = main_content.find("div", class_="container product-index product-index--filterable")
    
    # create DataFrame
    df = pandas.DataFrame()
    
    # iterate over all divs
    for content in product_list.findAll("div", class_ = re.compile("product-card tea")):
        tea_dict = {}
        print(content.find("h2", class_="product-card__title").find("span").text)
        
        # get link to product and price
        link_to_product = content.find("a", class_="product-card__image-link").get("href")
        tea_dict["Link"] = link_to_product
        
        # get data from link_to_product
        product_html = requests.get(link_to_product).text
        product_text = BeautifulSoup(product_html, "html.parser")
            
        # get body/main/product-info container/product-info__info
        product_info = product_text.find("div", class_="product-info container")
        tea_info = product_text.find("article", class_="product-article")
        brewing_instructions = product_text.find("div", class_ = "brewing-instructions torn-edges")
        
        # get name
        name = product_info.find("h1", class_ = "product-info__title").text
        tea_dict["Name"] = name
        
        # get type
        tea_type = content.find("span", class_="product-card__type").text
        tea_dict["Type"] = tea_type
            
        try:
            # get community score
            community_score = int(product_info.find("span", itemprop = "ratingValue").text)
            tea_dict["Score"] = community_score
                
            # get number of reviews
            number_of_reviews = int(product_info.find("meta", itemprop = "reviewCount").get("content"))
            tea_dict["Number of Reviews"] = number_of_reviews
        except:
            tea_dict["Score"] = 0
            tea_dict["Number of Reviews"] = 0
        
        # get price per gram
        prices_elements = product_info.findAll("div", class_ = "product-options__option")
        prices_per_gram = [float(safepricesearch(div, "span", class_ = "product-purchase-info__price-info")) for div in prices_elements]
        price_per_gram = min(prices_per_gram)
        tea_dict["Price per Gram"] = price_per_gram
        
        # get tasting notes
        try:
            tasting_notes = tea_info.find("dl", class_ = "product-tasting-notes__list")
            tasting_note_titles = tasting_notes.findAll("dt", class_= "product-tasting-notes__title")
            tasting_note_titles_list = [note.text for note in tasting_note_titles]
            
            tasting_note_contents = tasting_notes.findAll("dd", class_= "product-tasting-notes__info")
            tasting_note_contents_list = [contents.text for contents in tasting_note_contents]
            
            tasting_notes_dict = {title: contents for title, contents in zip(tasting_note_titles_list, tasting_note_contents_list)}
        
            # put tasting notes into tea_dict
            tea_dict.update(tasting_notes_dict)
        except:
            pass
        
        # get other info
        detail = tea_info.find("dl", class_ = "product-detail")
        detail_titles = detail.findAll("dt", class_= "product-detail__title")
        detail_titles_list = [note.text for note in detail_titles]
        
        detail_contents = detail.findAll("dd", class_= "product-tasting-notes__info")
        detail_contents_list = [contents.text for contents in detail_contents]
        
        details_dict = {title: contents for title, contents in zip(detail_titles_list, detail_contents_list)}
        
        tea_dict.update(details_dict)
        
        # get brewing instructions
        titles = ["Water Temperature", "GongFu g per 100ml", "GongFu First Infusion Seconds", "GongFu Additional Seconds", "GongFu No Infusions", "Western g per 100ml", "Western First Infusion Seconds", "Western Additional Seconds", "Western No Infusions"]
        try:
            instructions = brewing_instructions.findAll("span", class_ = "brewing-instructions__value")
            instructions_list = [float(re.findall(r'\d+', instruction.text)[0]) for instruction in instructions]
        except:
            instructions_list = [0.]*9
        instructions_dict = {title: contents for title, contents in zip(titles, instructions_list)}
        tea_dict.update(instructions_dict)
        
        df = df.append(tea_dict, ignore_index = True)
        
    print(df.head())
    df.to_csv("MeiLeaf_data.csv")
        
    
if __name__ == "__main__":
    main()
    
