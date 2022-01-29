import pandas as pd
from bs4 import BeautifulSoup
import urllib, pymysql, calendar, time, json
from urllib.request import urlopen
from datetime import datetime
from threading import Timer

class DBUpdater:
    def __init__(self):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='localhost', port=13306, user='root', password='qwaszx2689!', db='Investar', charset='utf8')

        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(40),
                last_update date,
                PRIMARY KEY (code))
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE if NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date))
            """
            curs.execute(sql)
        self.conn.commit()

        self.codes = dict()
        self.update_comp_info()

            
    def __del__ (self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close()

    def read_krx_code(self):
        """KRX로부터 상장법인목록 파일을 읽어와서 데이터프레임으로 반환"""
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'

        # 상장법인목록.xls 파일을 read_html() 함수로 읽는다.
        krx = pd.read_html(url, header=0)[0]
        # 종목코드 칼럼과 회사명만 남긴다. 데이터프레임에 [[]]을 사용하면 특정 칼럼만 뽑아서 원하는 순서대로 재구성 가능
        krx = krx[['종목코드', '회사명']]
        # 한글 칼럼명을 영문 칼럼명으로 변경한다.
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})
        # 종목코드 형식을 {:06d} 형식의 문자열로 변경한다.
        krx.code = krx.code.map('{:06d}'.format)

        return krx

    # 일반적으로 테이블에 데이터 행을 삽입하는 데 INSERT INTO 구문을 사용하지만, INSERT INTO 구문 역시 
    # 데이터 행이 테이블에 이미 존재하면 오류가 발생해 프로그램이 종료된다. 
    # 표준 SQL문은 아니지만 마리아디비에서 제공하는 REPLACE INTO 구문을 사용하면, 동일한 데이터 행이 존재하더라도
    # 오류를 발생하지 않고 UPDATE를 수행한다. REPLACE INTO 구문처럼 INSERT와 UPDATE를 합쳐놓은 기능을 UPSERT라고 부르기도한다.
    def update_comp_info(self):
        """종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장"""
        sql = 'SELECT * FROM company_info'
        # company_info 테이블을 read_sql() 함수로 읽는다.
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            # 위에서 읽은 데이터프레임을 이용해서 종목코드와 회사명으로 codes 딕셔너리를 만든다.
            self.codes[df['code'].values[idx]] = df['company'].values[idx]
        
        with self.conn.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            # SELECT max() ~구문을 이용해서 DB에서 가장 최근 업데이트 날짜를 가져온다.
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')

            # 위에서 구한 날짜가 존재하지 않거나 오늘보다 오래된 경우에만 업데이트한다.
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                # KRX 상장기업 목록파일을 읽어서 krx 데이터프레임에 저장한다.
                krx = self.read_krx_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO company_info (code, company, last_update) VALUES ('{code}', '{company}', '{today}')"
                    
                    # REPLACE INTO 구문을 이용해서 "종목코드, 회사명, 오늘날짜" 행을 DB에 저장한다.
                    curs.execute(sql)
                    # codes 딕셔너리에 '키-값'으로 종목코드와 회사명을 추가한다.
                    self.codes[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] {idx:04d} REPLACE INTO company_info VALUES ({code}, {company}, {today})")
                    
                    self.conn.commit()
                    print('')


    def read_naver(self, code, company, pages_to_fetch):
        """네이버 금융에서 주식 시세를 읽어서 데이터프레임으로 변환"""

    def read_into_db(self, df, num, code, company):
        """네이버 금융에서 읽어온 주식 시세를 DB에 REPLACE"""
    
    def update_daily_price(self, pages_to_fetch):
        """KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트"""

    def excute_daily(self):
        """실행 즉시 및 매일 오후 다섯시에 daily_price 데이블 업데이트"""

if __name__ == '__main__':
    dbu = DBUpdater()
    dbu.update_comp_info()
    #dbu.execute_daily()

# DBUpdater.py가 단독으로 실행되면 DBUpdater 객체를 생성한다. 
# DBUpdater의 생성자 내부에서 마리아디비에 연결한다.
# company_info 테이블에 오늘 업데이트된 내용이 있는지 확인하고, 없으면 (4) 를 호출하여 compay_info 테이블에 업데이트하고 codes 딕셔너리에도 저장한다.
# KRX로부터 상장법인 목록 파일을 읽어온다.