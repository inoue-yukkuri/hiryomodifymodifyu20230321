import streamlit as st
from PIL import Image
import pandas as pd
import pulp

st.title('肥料の最適くん【アプリ】')
st.caption('"作りたい野菜”と"家にある肥料”を選ぶと、"撒く肥料の最適な量"がわかります！') 

image=Image.open('23227773.png')
st.image(image, width=200)

st.subheader('↓こちらで計算できます↓')

#データのインポート
hiryou_df =pd.read_csv('hiryou0313.csv')
yasai_df =pd.read_csv('yasai0228.csv')

#リストの定義
hiryou = hiryou_df["hiryou"].tolist()
yasai = yasai_df["yasai"].tolist()

#入力フォーム表示
with st.form(key='profile_form'):
    
    #selectbox #radio
    c_yasai = st.selectbox(
        '1.作りたい野菜を選んでください(1つ)',
        yasai
    )

    #multiselect
    c_hiryou=st.multiselect(
        '2.使用できる肥料を選んでください　　※２つ以上(多いほど結果が安定します)',
        hiryou
    )
    
    st.text('3.計算ボタンを押してください')
    st.text('※結果は下に表示されます')
    #button
    submit_btn=st.form_submit_button('計算')
    cancel_btn=st.form_submit_button('リセット')
    st.text('※結果はこの下に表示されます↓')
    
#定数の定義
cost = {row.hiryou:row.Price for row in hiryou_df.itertuples()}
require = {row.yasai:(row.N, row.P, row.K, row.W) for row in yasai_df.itertuples()}
nutrition = {row.hiryou:(row.N, row.P, row.K,) for row in hiryou_df.itertuples()}
#yasai
c_yasai_req=require[c_yasai]
c_yasai_N=c_yasai_req[0]
c_yasai_P=c_yasai_req[1]
c_yasai_K=c_yasai_req[2]
c_yasai_W=c_yasai_req[3]
#hiryou
c_hiryo_list_N=[]
c_hiryo_list_P=[]
c_hiryo_list_K=[]
for h in c_hiryou:
    nutirition_sample=nutrition[h]
    c_hiryo_list_N.append(nutirition_sample[0])
    c_hiryo_list_P.append(nutirition_sample[1])
    c_hiryo_list_K.append(nutirition_sample[2])

#ボタンを押したあとの処理
if submit_btn:
    #計算
    problem = pulp.LpProblem('LP2', pulp.LpMinimize)
    #変数
    x = pulp.LpVariable.dicts('x', c_hiryou, cat='Continuous')

    #制約条件
    #各々の肥料は0～10㎏の範囲
    for h in c_hiryou:
        problem += x[h] >= 0
        problem += x[h] <= 10000

    #各々の成分誤差は0.1%以内
    problem += pulp.lpSum(c_hiryo_list_N[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) <= c_yasai_N+0.1
    problem += pulp.lpSum(c_hiryo_list_N[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) >= c_yasai_N-0.1
    problem += pulp.lpSum(c_hiryo_list_P[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) <= c_yasai_P+0.1
    problem += pulp.lpSum(c_hiryo_list_P[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) >= c_yasai_P-0.1
    problem += pulp.lpSum(c_hiryo_list_K[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) <= c_yasai_K+0.1
    problem += pulp.lpSum(c_hiryo_list_K[i]*x[c_hiryou[i]] for i in range(len(c_hiryou))) >= c_yasai_K-0.1

    #肥料の合計重量はc_yasai_W（2㎏ぐらい）以上→有機質考慮
    problem +=pulp.lpSum([x[h] for h in c_hiryou])>=c_yasai_W

    #目的関数（肥料の総費用）
    problem += pulp.lpSum([cost[h]*x[h] for h in c_hiryou])

    #解く
    status = problem.solve()


    #計算結果の表示
    st.subheader('計算結果')




    if pulp.LpStatus[status]=='Optimal':
      
      image=Image.open('yorokobi23167399.jpg')
      st.image(image, width=150)

      hituyouryou=[]
      for h in c_hiryou:
          round_h=round(x[h].value(),1)
          hituyouryou.append(f'{round_h}g')
      df_c={'肥料名':c_hiryou,'必要量（g/m²）':hituyouryou}
      df_c=pd.DataFrame(df_c)
      df_c=df_c.set_index('肥料名')
      st.dataframe(df_c)


      st.text('計算結果は1ｍ²（1m×1m）に\n'
              '撒く必要がある各々の重さ(g)です')

    
      st.text(f'1ｍ²あたりの肥料の総費用：約{round(problem.objective.value())}円')

      st.subheader('おしらせ')
      image=Image.open('23227773.png')
      st.image(image, width=200)
      st.write("畑やプランターの大きさに合った肥料の量を知りたい方はこちらのアプリで計算できます(無料)→ [肥料の最適くん（面積考慮ver）](https://inoue-yukkuri-hiryoumenseki20230317-main-app-ry704p.streamlit.app/)")


    else:
      image=Image.open('kanasimi23626979.jpg')
      st.image(image, width=200)
      st.text(f'Status,{pulp.LpStatus[status]}\n'
              'ごめんなさい！計算できませんでした')
      st.text('選んだ肥料の成分が偏っています\n'
              '肥料の種類を増やしてください')
      st.text('選ぶのが手間でしたら\n'
              'すべての肥料を選択してください\n'
              'その中から必要なものを自動で抜粋します')
      
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

st.write("・本アプリの計算データはこちらを参考にしています→ [農林水産省/都道府県施肥基準等/東京都施肥基準](https://www.agri.metro.tokyo.lg.jp/production/technical/fertilization/index.html)")
st.write("・本アプリはN・P・K・有機質の量を考慮した数理最適化問題（費用最小）として計算しています")
st.write("・質問や、追加してほしい機能などはこちらへ→ [お問い合わせ](https://forms.gle/7PWEB6JZAY4gU1fQ7)")
st.write("・農業のゆっくり解説をYouTubeでしてます。アプリの使い方、計算に使用した肥料なども紹介する予定です→ [YouTube](https://www.youtube.com/@yurunougyou)")



      
