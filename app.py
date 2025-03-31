from flask import Flask, request, render_template, url_for
import pandas as pd


#Flask 생성
app = Flask(__name__)

# 유저가 입력할 (종목, 투자기간, 투자 전략 방식을 입력하는)
@app.route('/invest')
def invest():
    return render_template('invest.html')

# 대쉬보드 확인하는 API
# 대쉬보드에서 필요한 데이터?
# table.cols( 컬럼의 데이터 ) list
# table_data( value의 값들 ) dict
# x_data 차트에서 x축 데이터 list
# y_data 차트에서 y축 데이터 list

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')






app.run(debug=True)
