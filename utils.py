import streamlit as st
import re
import requests

import pandas as pd
import pydeck as pdk


def get_llm_suggests(openai_client, country_input, month_input, region_input):
    completion = openai_client.chat.completions.create(
      model="gpt-3.5-turbo-0613",
      messages=[
        {"role": "user",
         "content": f"""
                        List best things to do in {region_input} {country_input} in {month_input},
                        and print out the suggested locations at the end in one line.
                    """}
      ]
    )
    output = completion.choices[0].message.content

    # get suggestions
    pattern = r'\d+\.\s+(.*)'
    try:
        suggestions = re.findall(pattern, output, re.MULTILINE)
    except:
        suggestions = []

    # get location list
    try:
        last_line = output.split('\n')[-1].replace('.', '').replace('-', '')
        location_lst = last_line.split(': ')[-1].split(', ')
    except:
        location_lst = []

    return location_lst, suggestions


def get_geo_json(location_lst, region, country):
    headers = {'User-Agent': st.secrets['PYDECK_UA']}

    output_lst = []
    for dest in location_lst:
        try:
            if 'and' in dest:
                dest = dest.split(' and ')[0]
            url = f"https://nominatim.openstreetmap.org/?addressdetails=1&q={dest}+{region}+{country}&format=json&limit=1"
            response = requests.get(url, headers=headers).json()
            output_lst.append({'lat': float(response[0]["lat"]),
                               'lon': float(response[0]["lon"]),
                               'tags': dest})
        except:
            try:
                dest = dest.split()[0]
                url = f"https://nominatim.openstreetmap.org/?addressdetails=1&q={dest}+{region}+{country}&format=json&limit=1"
                response = requests.get(url, headers=headers).json()
                output_lst.append({'lat': float(response[0]["lat"]),
                                   'lon': float(response[0]["lon"]),
                                   'tags': dest})
            except:
                pass

    if len(output_lst) > 0:
        return pd.DataFrame(output_lst)
    else:
        return None


def get_map(geo_df):
    ICON_URL = "https://img.icons8.com/plasticine/100/000000/marker.png"

    icon_data = {
        "url": ICON_URL,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }

    # can't assign icon_data to pandas column directly, otherwise it can't be shown on the map
    geo_df["icon_data"] = None
    for i in geo_df.index:
        geo_df["icon_data"][i] = icon_data
    view_state = pdk.data_utils.compute_view(geo_df[["lon", "lat"]])

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=geo_df,
        get_icon="icon_data",
        get_size=4,
        size_scale=20,
        get_position=["lon", "lat"],
        pickable=True,
    )

    r = pdk.Deck(layers=[icon_layer], initial_view_state=view_state, tooltip={"text": "{tags}"})
    return r


def search_images(query, api_key, cx, hq):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "searchType": "image",
        "key": api_key,
        "cx": cx,
        "num": 2,
        "imgType": ["photo"],
        "imgSize": ["huge", "xxlarge"],
        "filter": 1,
        "lr": "lang_en",
        "imgColorType": "color",
        "hq": hq
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        image_urls = [item["link"] for item in data.get("items", [])]
        return image_urls
    else:
        return []


def display_images(suggestion, max_query_ct, image_lst):
    st.write(suggestion)
    max_images_per_row = max_query_ct
    num_cols = min(max_images_per_row, len(image_lst))

    cols = st.columns(num_cols)
    for col, url in zip(cols, image_lst):
        col.image(url, use_column_width='auto')
