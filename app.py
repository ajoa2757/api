#필요한 패키지들 import
from flask import Flask, jsonify
from sqlalchemy import create_engine, text

#자동으로 이 함수를 통해서 Flask 가 run 된다.
#단위 테스트라는 과정에서 테스트용 데이터베이스를 사용하기 위해, text_config 라는 인자가 존재한다
#단위 테스트에 대해서는 나중에 더 알아보자
def create_app(test_config=None):
        app = Flask(__name__)

        # test_config 를 사용하지 않는 상황일 경우 config.py 로부터 읽는다.
        if test_config is None:
                app.config.from_pyfile("config.py")
        else:
                app.config.update(test_config)

        # test_config 를 사용하지 않는 상황일 경우 config.py 로부터 읽는다.
        database = create_engine(app.config['DB_URL'],encoding = 'utf-8',max_overflow=0)
        app.database = database

        return app