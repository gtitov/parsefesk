import requests
from bs4 import BeautifulSoup




def bs_from_url(url):
    text = requests.get(url).text
    clean_text = text.replace("&nbsp;", " ").replace("\xa0", " ")  # replace non-breaking space with regular space
    soup = BeautifulSoup(clean_text, 'html.parser')
    return soup


def get_wetlands_urls(index_url):
    index_soup = bs_from_url(index_url)
    anchors = index_soup.find_all("a")
    hrefs = [a.get("href") for a in anchors]
    wetlands_hrefs = list(filter(lambda href: href.startswith("http://www.fesk.ru/wetlands/"), hrefs))
    return wetlands_hrefs

# print(get_wetlands_urls("http://www.fesk.ru/list/index.html"))


def dms_to_decimal(dms_text):
    dms_list = dms_text.split(" ")
    dms_strings = dms_list[0].replace("''", "").replace("'", " ").replace("°", " ").split(" ")
    dms_values = [int(string) for string in dms_strings]
    dms_hemisphere = dms_list[1][0]  # very first letter defines hemisphere so take only the first letter
    k_hemisphere = {"с": 1, "в": 1, "ю": -1, "з": -1}  # k to set a hemisphere to decimal correctly
    k_dms = k_hemisphere[dms_hemisphere]
    decimal = k_dms * (dms_values[0] + dms_values[1] / 60 + dms_values[2] / 3600)
    return round(decimal, 5)


def get_wetland_data(wetland_url):
    wetland_soup = bs_from_url(wetland_url)
    name = wetland_soup.find("h1").text
    coords = wetland_soup.select("table.mm tr:nth-of-type(2) td:nth-of-type(5)")[0].text.split(", ")
    lat = dms_to_decimal(coords[0])
    lon = dms_to_decimal(coords[1])
    area = wetland_soup.select("table.mm tr:nth-of-type(2) td:nth-of-type(6)")[0].text
    try:
        area_ha = int(area.replace(" ", "").strip("га"))
    except ValueError:
        area_ha = ""
    # reason = wetland_soup.find("h4", text="Критерии включения в список").next_sibling.strip(".")
    reason = wetland_soup.select("table.mm tr:nth-of-type(2) td:nth-of-type(4)")[0].text
    wltype = wetland_soup.select("table.mm tr:nth-of-type(2) td:nth-of-type(3)")[0].text
    wetland_dict = {
        "name": name,
        "lon": lon,
        "lat": lat,
        "area_ha": area_ha,
        "reason": reason,
        "wltype": wltype,
        "url": wetland_url
    }
    print(wetland_url)
    return wetland_dict

# print(get_wetland_data("http://www.fesk.ru/wetlands/3.html"))


if __name__ == '__main__':
    wetland_pages = get_wetlands_urls("http://www.fesk.ru/list/index.html")
    wetlands_data = [get_wetland_data(url) for url in wetland_pages]
    header_row = ",".join(list(wetlands_data[0].keys()))
    with open("wetlands_fesk.csv", mode="w", encoding="utf-8") as f:
        f.write(header_row)
        for wetland_dict in wetlands_data:
            # quotes to preserve commas inside values
            string_wetland_list = ['"%s"' % str(value) for value in list(wetland_dict.values())]
            data_row = ",".join(string_wetland_list)
            f.write("\n")  # start with new line so there will be no extra new line at the end
            f.write(data_row)






