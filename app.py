from flask import Flask, request, jsonify, render_template, redirect
import logging
import json
import random
import os

print(os.getcwd())
app = Flask(__name__, template_folder="/app")

logging.basicConfig(level=logging.INFO)

# создаем словарь, в котором ключ — название города,
# а значение — массив, где перечислены id картинок,
# которые мы записали в прошлом пункте.

sessionStorage = {}


@app.route('/alica', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Будем учиться?'
        res["response"]["buttons"] = [
            {
                "title": "Да",
                "hide": True
            },
            {
                "title": "Нет",
                "hide": True
            }
        ]
        return
        # создаем словарь в который в будущем положим имя пользователя
    else:
        if "да" in req['request']['nlu']['tokens'] or "продолжаем" in req['request']['nlu']['tokens']:
            f = open("rewords.txt")
            words = [" ".join(x.split(sep=",")) for x in f]
            ans = random.choices(words, k=5)
            while not all(len(x.split()) == 3 for x in ans):
                ans = random.choices(words, k=5)
            res['response']['text'] = " ".join(ans)
            print(ans)
            print(ans[0].split())
            res["response"]["buttons"] = [
                {
                    "title": "Продолжаем",
                    "hide": True,
                },
                {
                    "title": "Стоп",
                    "hide": True,
                },
                {
                    "title": "".join(ans[0].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[1].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[2].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[3].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[4].split()[1]),
                    "hide": True
                }
            ]
            sessionStorage["suggests"] = [{
                "title": "Продолжаем",
                "hide": True,
            },
                {
                    "title": "Стоп",
                    "hide": True,
                },
                {
                    "title": "".join(ans[0].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[1].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[2].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[3].split()[1]),
                    "hide": True
                },
                {
                    "title": "".join(ans[4].split()[1]),
                    "hide": True
                }
            ]
            f.close()
            return

        elif "нет" in req['request']['nlu']['tokens'] or "стоп" in req['request']['nlu']['tokens']:
            res['response']['text'] = "Прощайте"
            res["response"]["end_session"] = True
            return
        else:
            if req['request']['nlu']['tokens'][0] in [x["title"] for x in sessionStorage["suggests"]] and len(
                    sessionStorage["suggests"]) > 2:
                sugg = req['request']['nlu']['tokens'][0]
                print(sugg)
                res['response']['text'] = sugg
                res['response']['tts'] = sugg
                sessionStorage["suggests"].pop([x["title"] for x in sessionStorage["suggests"]].index(sugg))
                print(sessionStorage["suggests"])
                res["response"]["buttons"] = sessionStorage["suggests"]
                return
            else:
                res['response']['text'] = "Не поняла, попробуйте еще раз"
                res["response"]["buttons"] = sessionStorage["suggests"]
                return


@app.route("/edit", methods=["GET", "POST"])
def editor():
    if request.method == "GET":
        content = []
        f = open("rewords.txt", encoding="utf-8")
        for x in f:
            one = x.split(sep=",")
            if len(one) == 3:
                content.append({
                    "number": one[0],
                    "en": one[1],
                    "ru": one[2].replace("\n", "")
                })
        f.close()
        return render_template("index.html", words=content)
    if request.method == "POST":
        word = [request.form["number"], request.form["en"], request.form["ru"]]
        writer = []
        f = open("rewords.txt", encoding="utf-8", mode="r")
        for x in f:
            if x != "\n":
                if int(x.split(sep=",")[0]) == int(word[0]):
                    word[0] = word[0] + 1
                else:
                    writer.append(x)
        writer.append(",".join(word))
        writer.sort(key=lambda x: int(x.split(sep=",")[0]))
        f.close()
        f = open("rewords.txt", encoding="utf-8", mode="w")
        for z in writer:
            if len(z) >= 3:
                print(z, file=f)
        f.close()
        return redirect("/edit")


@app.route("/delete/<number>", methods=["GET"])
def deleter(number):
    writer = []
    f = open("rewords.txt", encoding="utf-8", mode="r")
    for x in f:
        if x != "\n":
            if int(x.split(sep=",")[0]) == int(number):
                pass
            else:
                writer.append(x)
    f.close()
    f = open("rewords.txt", encoding="utf-8", mode="w")
    for z in writer:
        if len(z) >= 3:
            print(z, file=f)
    f.close()
    return redirect("/edit")


if __name__ == '__main__':
    app.run()
