# U-9-and-19-Project
Game Setup (on Gaming PC or Laptop)
Step 1: Install Python
1.	Download from: https://www.python.org/downloads
2.	During installation, check “Add Python to PATH”.
________________________________________
Step 2: Install Game Dependencies
Open Command Prompt or Terminal and run:
pip install pygame numpy

Set Up AntiMicro (Controller to Keyboard Mapping)

Install AntiMicro:
•	Windows: https://github.com/AntiMicro/antimicro/releases
•	Linux (Debian-based):
sudo apt install antimicro
Map Controller:
1.	Open AntiMicro and plug in your joystick/controller.
2.	Assign joystick buttons to keys used in your game (A, B, C, D).
Important: Make sure AntiMicro is running while the game is being played.

Leaderboard Server Setup (on Raspberry Pi)
✅ Step 1: Install Flask on Raspberry Pi
Open the Pi terminal:
sudo apt update
sudo apt install python3-pip
pip3 install flask
________________________________________
✅ Step 2: Create the Flask App
1.	Make a folder for the leaderboard server:
mkdir leaderboard_server
cd leaderboard_server
2.	Create a file called app.py with this sample Flask code:
python
from flask import Flask, request, jsonify
app = Flask(__name__)

scores = []

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    name = data.get("name")
    score = data.get("score")
    if name and isinstance(score, int):
        scores.append({"name": name, "score": score})
        scores.sort(key=lambda x: x["score"], reverse=True)
        return jsonify({"message": "Score submitted!"}), 200
    return jsonify({"error": "Invalid input"}), 400

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    return jsonify(scores[:10])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
3.	Run the server:
python3 app.py
Now your leaderboard is live on your Pi at:
arduino
http://<your_pi_ip>:5000/leaderboard
________________________________________
✅ Game → Server Integration Notes
•	The game uses HTTP POST to send scores to the Pi’s Flask server (/submit).
•	You had an issue with a wrong URL before — make sure you POST to:
arduino
http://<your_pi_ip>:5000/submit
________________________________________
