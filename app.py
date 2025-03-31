from flask import Flask, request, render_template, url_for,redirect, session
import pandas as pd
import invest
from database import MyDB
import os
from data import querys
from dotenv import load_dotenv

#.env 파일 로드
load_dotenv()

#Flask 생성
app = Flask(__name__)

#session 비밀키 지정
app.secret_key = os.getenv('secret')


# database_class 생성
mydb = MyDB(
    _host = os.getenv('host'),
    _port = int(os.getenv('port')),
    _user = os.getenv('user'),
    _password = os.getenv('pwd'),
    _db = os.getenv('db')
)

# 테이블 생성하는 쿼리 생성
mydb.execute_query(querys.create_query)

# /api 생성
@app.route('/')
def index():
    return render_template('index.html')

#회원가입 페이지로 이동
@app.route('/signup')
def signup():
    return render_template('signup.html')

#로그인 api
@app.route('/signin', methods=['post'])
def signin():
    input_id = request.form['id']
    input_pass = request.form['password']
    login_result = mydb.execute_query(querys.login_query,input_id,input_pass)
    if len(login_result) == 1:
        print('로그인 성공')
        # 세션데이터 저장
        session['user_info'] = [input_id,input_pass]
        return redirect('/invest')
    else:
        return redirect('/')


#회원가입 api
@app.route('/signup2', methods=['post'])
def signup2():
    #id, password, name 데이터를 받아온다.
    input_id = request.form['id']
    input_pass = request.form['password']
    input_name = request.form['name']
    
    # 사용가능한 아이디인가 확인
    check_result = mydb.execute_query(querys.check_query, input_id)
    if len(check_result) == 0:
        # 사용 가능 아이디
        mydb.execute_query(querys.signup_query, input_id, input_pass, input_name,inplace=True)
        return redirect('/')
    else:
        print('중복된 아이디가 존재합니다.')
        return redirect('/signup')
    



# 유저가 입력할 (종목, 투자기간, 투자 전략 방식을 입력하는)
@app.route('/invest')
def first():
    if 'user_info' in session:
        return render_template('invest.html')
    else:
        return redirect('/')

# 대쉬보드 확인하는 API
# 대쉬보드에서 필요한 데이터?
# table.cols( 컬럼의 데이터 ) list
# table_data( value의 값들 ) dict
# x_data 차트에서 x축 데이터 list
# y_data 차트에서 y축 데이터 list

@app.route('/dashboard')
def dashboard():
    if 'user_info' not in session:
        return redirect('/')
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
