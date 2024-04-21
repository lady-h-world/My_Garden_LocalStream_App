import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="explore_local_traveling")
with st.sidebar:
    st.image('logo.png', width=200)
    st.markdown('#')
    st.session_state.openai_api_key = st.text_input("Enter OpenAI API Key", key="chatbot_api_key", type="password")
    "[How to get OpenAI API key](https://platform.openai.com/account/api-keys)"

    st.write(f'{TEST_CODE}')

st.title("💖 Where do you plan to travel to?")
st.markdown('#')

# Set default values
if 'show_region' not in st.session_state.keys():
    st.session_state.show_region = 'No'


# Build user input form
col1, col2 = st.columns(2)
with col1:
    def country_submit():
        """
        empty text_input after submit the country
        """
        st.session_state.country = st.session_state.country_in
        st.session_state.country_in = ''

    country = st.text_input(
        label="📍 Country",
        key='country_in',  # this is the key for streamlit session_state
        placeholder="Enter Destination Country",
        on_change=country_submit
    )

    if 'country' in st.session_state.keys() and st.session_state.country != '':
        show_region = st.radio(
            f'Any specific city or region in {st.session_state.country} ?',
            ['Yes', 'No'],
            key='show_region',
            index=1,
        )
        if st.session_state.show_region == 'Yes':
            def region_submit():
                """
                empty text_input after submit the region
                """
                st.session_state.region = st.session_state.region_in
                st.session_state.region_in = ''

            region = st.text_input(
                label="📍 Region",
                key='region_in',  # this is the key for streamlit session_state
                placeholder="Enter Destination Region",
                on_change=region_submit
            )

with col2:
    def month_submit():
        """
        empty select_box after selected month
        """
        st.session_state.month = st.session_state.month_in
        st.session_state.month_in = None

    traveling_month = st.selectbox(
        label="🗓️ Select Traveling Month",
        key='month_in',
        index=None,
        options=('January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December'),
        on_change=month_submit
    )


st.markdown('#')
country_input, region_input, month_input = '____', '', '____'
if 'country' in st.session_state.keys() and st.session_state.country != '':
    country_input = st.session_state.country
if st.session_state.show_region == 'Yes':
    if 'region' in st.session_state.keys() and st.session_state.region != '':
        region_input = st.session_state.region
    else:
        region_input = '____'
if 'month' in st.session_state.keys() and st.session_state.month != None:
    month_input = st.session_state.month
if country_input != '____' or region_input not in ['____', ''] or month_input != '____':
    confirm_response = f"""#### 🤩 You plan to travel to: <u>{region_input}</u> <u>{country_input}</u> in month <u>{month_input}</u>"""
    st.markdown(confirm_response, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col4:
        st.markdown('#')
        if st.button('Clear Messages'):
            if 'country' in st.session_state.keys():
                del st.session_state['country']
            if 'month' in st.session_state.keys():
                del st.session_state['month']
            if 'region' in st.session_state.keys():
                del st.session_state['region']
            st.rerun()

    if (st.session_state.show_region == 'No' and country_input != '____' and month_input != '____') or \
       (st.session_state.show_region == 'Yes' and country_input != '____' and month_input != '____' and region_input not in ['____', '']):
        with col3:
            st.markdown('#')
            if not st.session_state.openai_api_key:
                guidance = '👈 Enter OpenAI API Key, then click <b>CONFIRM</b>'
                st.markdown(guidance, unsafe_allow_html=True)
            else:
                if st.button('CONFIRM'):
                    switch_page('results')


