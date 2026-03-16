from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import pandas as pd
import os

app = Flask(__name__)

excel_file = "appointments.xlsx"

if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Phone", "Name", "Problem", "Date"])
    df.to_excel(excel_file, index=False)


@app.route("/voice", methods=["POST"])
def voice():

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/get_name",
        method="POST",
        language="hi-IN",
        speechModel="phone_call"
    )

    gather.say(
        "Namaste Lakshya Clinic me aapka swagat hai. Kripya apna naam bataye.",
        language="hi-IN"
    )

    response.append(gather)

    return str(response)


@app.route("/get_name", methods=["POST"])
def get_name():

    name = request.form.get("SpeechResult")
    phone = request.form.get("From")

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action=f"/get_problem?name={name}&phone={phone}",
        method="POST",
        language="hi-IN",
        speechModel="phone_call"
    )

    gather.say(
        f"Dhanyavaad {name}. Kripya apni problem bataye.",
        language="hi-IN"
    )

    response.append(gather)

    return str(response)


@app.route("/get_problem", methods=["POST"])
def get_problem():

    name = request.args.get("name")
    phone = request.args.get("phone")
    problem = request.form.get("SpeechResult")

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action=f"/get_date?name={name}&phone={phone}&problem={problem}",
        method="POST",
        language="hi-IN",
        speechModel="phone_call"
    )

    gather.say(
        "Aap appointment kis date ke liye lena chahte hain?",
        language="hi-IN"
    )

    response.append(gather)

    return str(response)


@app.route("/get_date", methods=["POST"])
def get_date():

    name = request.args.get("name")
    phone = request.args.get("phone")
    problem = request.args.get("problem")
    date = request.form.get("SpeechResult")

    df = pd.read_excel(excel_file)

    new_data = pd.DataFrame([{
        "Phone": phone,
        "Name": name,
        "Problem": problem,
        "Date": date
    }])

    df = pd.concat([df, new_data], ignore_index=True)

    df.to_excel(excel_file, index=False)

    response = VoiceResponse()

    response.say(
        "Dhanyavaad. Aapka appointment request register ho gaya hai.",
        language="hi-IN"
    )

    return str(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
