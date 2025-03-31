from flask import Flask, request, render_template, url_for
import pandas as pd
import invest
from database import MyDB


#Flask 생성
app = Flask(__name__)

# database_class 생성
mydb = MyDB()

# 유저가 입력할 (종목, 투자기간, 투자 전략 방식을 입력하는)
@app.route('/invest')
def first():
    return render_template('invest.html')

# 대쉬보드 확인하는 API
# 대쉬보드에서 필요한 데이터?
# table.cols( 컬럼의 데이터 ) list
# table_data( value의 값들 ) dict
# x_data 차트에서 x축 데이터 list
# y_data 차트에서 y축 데이터 list

@app.route('/dashboard')
def dashboard():
    # get 방식으로 받아온 데이터 -> request.args
    # post 였다면? request.form
    input_code = request.args['code']
    
    #시작 시간
    input_year = request.args['year']
    input_month = request.args['month']
    input_day = request.args['day']
    input_time = f'{input_year}-{input_month}-{input_day}'
    
    # 투자 방식
    input_type = request.args['type']
    # 데이터 로드
    df = invest.load_data(input_code, input_time)
    # class 생성
    invest_class = invest.Invest(df,_col='Close',_start = input_time)
    # input_type 기준으로 class의 함수 호출
    if input_type == 'bnh':
        result = invest_class.buyandhold()
    elif input_type == 'boll':
        result = invest_class.bollinger()
    elif input_type == 'mmt':
        result = invest_class.momentum()
    # 특정 컬럼만 필터
    result = result[['Close','trade','rtn','acc_rtn']]
    
    # 특정 컬럼 생성
    result['ym'] = result.index.strftime('%Y-%m')
    # 테이블 정제
    # 한 달 중에 가장 높은 종가, 
    result = pd.concat(
        [
            result.groupby('ym')[['Close','trade','acc_rtn']].max(),
            result.groupby('ym')[['rtn']].mean()
        ], axis=1
    )
    result.reset_index(inplace=True, drop=False)
    #컬럼 이름 변경
    result.columns = ['시간','종가','보유내역','누적 수익률','일별 수익률']
    
    
    # 컬럼
    cols_list = list(result.columns)
    # 테이블에 데이터를 넣기 위해 딕셔너리 형태로 변환
    dict_data = result.to_dict(orient='records')
    # x축 데이터
    x_data = list(result['시간'])
    y_data = list(result['일별 수익률'])
    y1_data = list(result['누적 수익률'])
    
    return render_template('dashboard.html',
                           table_cols= cols_list,
                           table_data = dict_data,
                           x_data = x_data,
                           y_data = y_data,
                           y1_data = y1_data
    )


app.run(debug=True)
