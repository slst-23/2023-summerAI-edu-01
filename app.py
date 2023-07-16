import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import openai
from openai.error import OpenAIError

st.title('🔎부산광역시 지역특화거리 찾기')

# Sidebar - 도움말
st.sidebar.title('🧚도움말')
st.sidebar.subheader('🔎지역특화거리 정보 조회')
st.sidebar.write('- 지도 위의 마커를 클릭하면 거리 이름과 간략한 소개를 확인할 수 있어요')
st.sidebar.write('- 지도 아래의 자세히 보기를 통해 더 많은 정보를 확인할 수 있어요')
st.sidebar.subheader('🤖챗봇 Q&A')
st.sidebar.write('- 지역특화거리에 대해 추가로 궁금한게 있다면 질문해보세요')
st.sidebar.write('- "submit"을 누른 후 기다리면 답변을 받아볼 수 있어요')

# Tab - 지역특화거리정보조회 / Q&A
tab1, tab2 = st.tabs(['🔎조회', '🤖Q&A'])

with tab1:
    st.title('Information')
    st.subheader('🗺️지역특화거리 정보를 확인하세요!')

    # 데이터 가져오기
    data = pd.read_csv('data.csv')
    # 지도생성
    m = folium.Map(location=[35.163884, 129.028591],
                   zoom_start=12)

    for i in range(len(data)):
        message = '<b>거리명 : </b>' + data['거리명'][i] + '<br><b>거리소개 : </b>' + data['거리소개'][i]
        iframe = folium.IFrame(message)
        popup = folium.Popup(iframe,
                             min_width=300,
                             max_width=300)
        folium.Marker(
            [data['위도'][i], data['경도'][i]],
            icon = folium.Icon(color='red'),
            popup = popup,
            tooltip=data['거리명'][i],
            color='red'
        ).add_to(m)

    st_data = st_folium(m, width=725)

    # Expander - 자세한 정보 확인
    with st.expander('자세히 보기'):
        st.dataframe(data[['거리명', '거리소개', '소재지도로명', '소재지지번주소', '점포수']])
with tab2:
    st.title('Q&A')
    st.subheader('💭궁금한게 있다면 물어보세요!')

    message = """
    부산의 지역특화거리에 대해 알려드리겠습니다.
    """

    messages = [{"role": "system", "content": message}]

    def clear_submit():
        st.session_state["submit"] = False

    def ask(q):
        q = {"role": "user", "content": q}
        messages.append(q)

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages
                                                )

        res = response.to_dict_recursive()
        bot_text = response['choices'][0]['message']['content']
        bot_input = {"role": "assistant", "content": bot_text}

        messages.append(bot_input)

        return bot_text

    # Load your API key from an environment variable or secret management service
    openai.api_key = "--Your API Key--"

    query = st.text_area('질문 입력 후 submit을 눌러주세요', value="지역특화거리에 대해 추가로 궁금한 점이 있다면 질문해보세요!", on_change=clear_submit)
    button = st.button("submit")

    if button or st.session_state.get("submit"):
        st.session_state["submit"] = True

        try:
            with st.spinner("답변 준비 중..."):
                ans = ask(query)

            st.markdown("#### 🤖 :")
            st.markdown(ans)

        except OpenAIError as e:
            st.error(e._message)
