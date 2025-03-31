# DataBase에 접속하여 query문을 보내는 함수까지 결합하여 클래스를 하나 생성

import pymysql
import pandas as pd

# class 선언
class MyDB:
    # 독립적으로 저장이 되는 변수 저장
    # class가 생성되는 과정에서 저장
    # 변수 : 서버주소, 포트번호, 유저명, 비밀번호, db명
    # 변수들의 기본값을 설정 ( 기본값은 rocal PC )
    def __init__(self,
                 _host = '127.0.0.1',
                 _port=3306,
                 _user='root',
                 _password='1234',
                 _db = 'mysql_table'):
        self.host = _host
        self.port = _port
        self.user = _user
        self.password = _password
        self.db = _db
        
    # 서버와 연결하고 커서를 생성하는 함수
    def connect_sql(self):
        # 서버와 연결
        self.server = pymysql.connect(
            host= self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            db = self.db
        )
        # 커서 생성
        self.cursor = self.server.cursor(pymysql.cursors.DictCursor)
        
    # 서버와 연결을 끊는 함수
    def close_sql(self):
        self.server.close()
        
    # 쿼리문을 실행하는 함수
    def execute_query(self,sql_query, *values, inplace=False):
        # 서버와 연결한다
        self.connect_sql()
        
        # 커서에 sql 쿼리를 보낸다.
        self.cursor.execute(sql_query,values)
        # sql_query가 select 문이라면?
        # if sql_query.upper().lstrip().startswith('SELECT'):
        if sql_query.upper().split()[0] == 'SELECT':
            # 커서에서 데이터 조회하기
            sql_data = self.cursor.fetchall()
            # 데이터프레임으로 변환
            result = pd.DataFrame(sql_data)
            
        else:
            # insert, update, delete이 경우
            # inplace가 true인 경우
            if inplace:
                self.server.commit()
            result = "Query OK" 
        
        # 서버와의 연결 종료
        self.close_sql()
            
        return result