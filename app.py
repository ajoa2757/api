from flask import Flask, jsonify, request
from flask.json import JSONEncoder

app = Flask(__name__)

#set 자료형이 포함되면 jsonify 형태로 동작을 하지 못하는 문제가 있다
#이것을 위한 custom 인코더라고 한다.
class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
                if isinstance(obj, set):
                        return list(obj)
                return JSONEncoder.default(self, obj)


app.json_encoder = CustomJSONEncoder


#사용자들의 정보가 담길 dictionaty.
#여기에 dictionary 의 dictionary 가 담길 것이다
app.users = {}

#users 의 index 라고 하던지 아니면 key 라고 하던지 로 쓰일 값이다.
#다만 이것은 큰 시스템 안에서는 오류를 일으킬 소지가 있다.
#제대로된 데이터베이스 시스템을 사용하면서 이 문제는 해결 될 것이다
app.id_count = 1
app.tweets = []

#팔로우 관계를 정리할 데이터베이스?

@app.route("/ping", methods = ['GET'])
def ping():
        return "pong"



@app.route("/sign-up",methods = ['POST'])
def sign_up():
        #json 은 http 요청에 사용될 수 있는 dictionary 의 형태이다.
        #이 new_user 는 그러니까 dictionary 형태로 받아온 데이터 이다.
        # 이로부터 여러 field 의 값들을 가져다 쓸 것이다.
        new_user = request.json

        #가령 id field 에 전달된 값은 이렇게 활용이 된다.
        new_user["id"] = app.id_count

        #위에서 추가한 바 있는 users list 에 new user 라는 요청이 담긴다.
        app.users[app.id_count]= new_user

        #내부적으로 id_count 가 처리되는 모습
        app.id_count = app.id_count +1

        return jsonify(new_user)

@app.route("/tweet", methods=['POST'])
def tweet():

        #payload dictionary 가 가져와지고 있다
        #요청으로부터 받은 여러 데이터들이 담긴다
        payload = request.json

        #임시변수들에 payload 로부터 값들이 가져와 지고 있다
        #특히 id 의 경우 int 로 강제형변환 당하고 있는 모습
        user_id = int(payload['id'])
        tweet = payload['tweet']

        #users dictionary 에서 user_id key 값이 있는지 탐색한다.
        #dictionary in 키워드는 key 를 키준으로 탐색한다
        if user_id not in app.users:
                return '사용자가 존재하지 않습니다', 400
        if len(tweet)>300:
                return '300자를 초과했습니다', 400

        #user_id 임시변수가 왜인지 다시 값을 가져오고 있는 모습?
        user_id = int(payload['id'])

        #{}괄호 안에 들어있으므로, 생성된 딕셔너리이다
        #그러니까 tweets 의 구조는 dictionary 의 list 인 것이다.
        #그리고 각각 dictionary 들은 user id 와 tweet 이렇게 두개의 key 를 가진다
        app.tweets.append({
                'user_id' :user_id,
                'tweet':tweet
        })

        #여기까지 왔을 때의 정상적인 출력
        return '',200

@app.route("/follow", methods=['POST'])
def follow():

        #마찬가지로 payload 변수에 request 에서 전달된 변수를 담는다
        #json 은 list 의 형태로 사용자가 제출한 정보를 잘 담는다
        payload = request.json
        user_id = int(payload['id'])
        user_id_to_follow = int(payload['follow'])

        #파이썬은 마치 모든 변수가 참조자인 것 처럼 동작하는 듯 하다?
        #아래 코드를 통해 user 는 마치 app.users[user_id] 의 참조자처럼 동작한다
        user = app.users[user_id]

        #setdefault 는 1번째 인자가 key 로서 존재한다면 그 value 를 리턴한다
        #만약 존재하지 않으면 2번째 인자를 value 로서 생성하고 또 그 value 를 리턴한다
        #아래 코드로 생성된 빈 set 가 리턴되거나, 이미 존재하는 follow 의 set 이 리턴되는 것이다.
        user.setdefault('follow',set()).add(user_id_to_follow)

        return jsonify(user)

@app.route("/unfollow", methods=['POST'])
def unfollow():

        #전반적으로 follow 와 유사한 동작인데 add 대신 discard 한다.

        payload = request.json
        user_id = int(payload['id'])
        user_id_to_unfollow = int(payload['unfollow'])

        user = app.users[user_id]
        user.setdefault('follow',set()).discard(user_id_to_unfollow)

        return jsonify(user)


if __name__ =='__main__':
        app.run()




