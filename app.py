from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to my Flask API!"

@app.route('/student')
def get_student():
    return jsonify({
        "name": "Your Name",
        "grade": 10,
        "section": "Zechariah"
    })

# Example cleaned-up Edge tabs metadata
edge_all_open_tabs = [
    {
        "pageTitle": "Google Gemini",
        "pageUrl": "https://gemini.google.com/u/6/app/5fe9cf9f3d140785?pageId=none",
        "tabId": 1472304481,
        "isCurrent": True
    },
    {
        "pageTitle": "Student Dashboard Pro",
        "pageUrl": "https://kikay.onrender.com/students",
        "tabId": 1472304800,
        "isCurrent": False
    },
    {
        "pageTitle": "ELECT 4A SIA Arduino",
        "pageUrl": "https://classroom.google.com/u/1/c/ODM4OTA0MTEyNTU2",
        "tabId": 1472304829,
        "isCurrent": False
    },
    {
        "pageTitle": "axcel ・ Web Service ・ Render Dashboard",
        "pageUrl": "https://dashboard.render.com/web/srv-d6sju5450q8c73fkuvqg/deploys/dep-d6sjv92a214c73bgqas0",
        "tabId": 1472304815,
        "isCurrent": False
    },
    {
        "pageTitle": "Facebook",
        "pageUrl": "https://www.facebook.com",
        "tabId": 1472304498,
        "isCurrent": False
    },
    {
        "pageTitle": "axcel/app.py at main · arelladoaxcel20-beep/axcel",
        "pageUrl": "https://github.com/arelladoaxcel20-beep/axcel/blob/main/app.py",
        "tabId": 1472304427,
        "isCurrent": False
    }
]

if __name__ == '__main__':
    app.run(debug=True)
