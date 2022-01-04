#필요한 패키지들 import
from flask      import Flask, request, jsonify, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

## Default JSON encoder는 set를 JSON으로 변환할 수 없다.
## 그럼으로 커스텀 엔코더를 작성해서 set을 list로 변환하여
## JSON으로 변환 가능하게 해주어야 한다.
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)


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

        #create_app 안에 정의된 sign-up 엔드포인트
        @app.route("/sign-up",methods=['POST'])
        def sign_up():

                #5장 미니터에서와 같은 방식으로 데이터 받아야 함
                new_user = request.json

                #execute : SQL 코드를 실행시킨다.
                #INSERT 명령어를 사용한다
                new_user_id = app.database.execute(text("""
                   INSERT INTO users(
                      name,
                      email,
                      profile,
                      hashed_password
                      --VALUES 가 new_user(json타입)으로부터 참조되는 것 주의!
                ) VALUES (
                      :name,
                      :email,
                      :profile,
                      :password
                      )
                    --lastrowid 는 auto increment 가 실행된 로우의 값을 return 한다
                    --이때 auto increment 가 있었던 값은 miniter-users 의 id 이겠지
                """),new_user).lastrowid

                #http 응답에 사용하기 위해, 추가된 로우를 참조한다.
                #SELECT 명령어로 하여금 READ 한다
                row = current_app.database.execute(text("""
                   SELECT 
                      id,
                      name,
                      email,
                      profile
                   FROM users
                   --WHERE 로 하여금 새로 삽입된 id 의 user 를 특정하여 READ 한다. 
                   WHERE id =:user_id
                """),{
                   'user_id' : new_user_id
                }).fetchone()

                #row 에서 읽은 정보를 딕셔너리로 변환한다.
                created_user = {
                        'id' : row['id'],
                        'name' : row['name'],
                        'email' : row['email'],
                        'profile' : row['profile']
                }if row else None
                return jsonify(created_user)

        return app

        @app.route('/tweet',methods=['POST'])
        def tweet():
            user_tweet = request.json
            tweet = user_tweet['tweet']

            if len(tweet)>300:
                    return '300자를 포함했습니다',400

            app.database.execute(text("""
               INSERT INTO tweets(
                  user_id,
                  tweet
               ) VALUES (
                  :id,
                  :tweet
               )
            """),user_tweet)

            return '',200




