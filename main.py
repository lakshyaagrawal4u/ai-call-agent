from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

excel_file = "appointments.xlsx"

if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Phone", "Name", "Problem"])
    df.to_excel(excel_file, index=False)


def ai_reply(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a polite clinic voice assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


@app.route("/voice", methods=["POST"])
def voice():

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/get_name",
        method="POST",
        speechTimeout="auto"
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
        action="/get_problem",
        method="POST",
        speechTimeout="auto"
    )

    gather.say(
        f"Dhanyavaad {name}. Kripya apni problem bataye.",
        language="hi-IN"
    )

    response.append(gather)

    response.redirect(f"/get_problem?name={name}&phone={phone}")

    return str(response)


@app.route("/get_problem", methods=["POST"])
def get_problem():

    name = request.args.get("name")
    phone = request.args.get("phone")
    problem = request.form.get("SpeechResult")

    # Save to Excel
    df = pd.read_excel(excel_file)

    new_data = pd.DataFrame([{
        "Phone": phone,
        "Name": name,
        "Problem": problem
    }])

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(excel_file, index=False)

    response = VoiceResponse()

    msg = ai_reply(
        f"Patient name is {name} and problem is {problem}. Reply politely confirming appointment."
    )

    response.say(msg, language="hi-IN")

    return str(response)


if __name__ == "__main__":
    app.run(port=5000)