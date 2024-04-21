import streamlit as st
import time
import sys
import requests
from PIL import Image
from io import BytesIO

from openai import OpenAI
from apify_client import ApifyClient

sys.path.append('../utils.py')
from utils import *


st.set_page_config(page_title="local_suggestions")
with st.sidebar:
    st.image('logo.png', width=200)

TIMEOUT_SECONDS = 180  # Timeout after 180 sec
MAX_QUERY_CT = 2

if 'country' in st.session_state.keys() and st.session_state.country != '' and \
       'month' in st.session_state.keys() and st.session_state.month != '':
    if 'region' not in st.session_state.keys() or st.session_state.region in ['____', ''] or st.session_state.show_region=='No':
        st.session_state.region = ''
    confirm_response = f"""#### 🤩 You plan to travel to: <u>{st.session_state.region}</u> <u>{st.session_state.country}</u> in month <u>{st.session_state.month}</u>"""
    st.markdown(confirm_response, unsafe_allow_html=True)

    openai_client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
    apify_client = ApifyClient(st.secrets['APIFY_CLIENT'])

    start_time = time.time()

    st.write('##')
    with st.spinner('🚀 Generating suggestions...'):
        location_lst, suggestion_lst = get_llm_suggests(openai_client,
                                                        st.session_state.country,
                                                        st.session_state.month,
                                                        st.session_state.region)
        if len(location_lst) == 0 and len(suggestion_lst) == 0:
            st.write("😵 Can't find any suggestion, would you like to adjust your input?")
            st.stop()

    if len(location_lst) > 0:
        with st.spinner('🚀 Loading suggestions on the map! Look 👇'):
            geo_df = get_geo_json(location_lst, st.session_state.region, st.session_state.country)
            if geo_df is not None:
                st.pydeck_chart(get_map(geo_df))
            else:
                st.write("🤔 Can't show anything on the map, does it exist on Earth?")

    if len(suggestion_lst) > 0:
        st.write('##')
        with st.spinner('🚀 Collecting local activities! Look 👇'):
            for suggestion in suggestion_lst:
                elapsed_time = time.time() - start_time
                if elapsed_time > TIMEOUT_SECONDS:
                    st.stop()  # stop when timeout

                run_input = {
                    "queries": [f'{suggestion} {st.session_state.region} {st.session_state.country} in {st.session_state.month}'],
                    "maxResultsPerQuery": MAX_QUERY_CT,
                }
                run = apify_client.actor("tnudF2IxzORPhg4r8").call(run_input=run_input)
                image_lst = []
                for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
                    try:
                        response = requests.get(item['imageUrl'], timeout=3)
                        if response.status_code == 200:
                            image_lst.append(Image.open(BytesIO(response.content)))
                    except:
                        pass
                if len(image_lst) > 0:
                    st.write(suggestion)
                    max_images_per_row = MAX_QUERY_CT
                    num_cols = min(max_images_per_row, len(image_lst))

                    cols = st.columns(num_cols)
                    for col, url in zip(cols, image_lst):
                        col.image(url, use_column_width='auto')

    st.stop()
