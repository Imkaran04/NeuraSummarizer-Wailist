from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import json

app = Flask(__name__)

# Database Configuration
WAITLIST_DB_URL = "sqlite:///./waitlist.db"
SURVEY_DB_URL = "sqlite:///./survey.db"

# Separate Base Models for Each DB
BaseWaitlist = declarative_base()
BaseSurvey = declarative_base()

# ========================= WAITLIST MODEL ========================= #
class Waitlist(BaseWaitlist):
    __tablename__ = "waitlist"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_no = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=True)
    occupation = Column(String, nullable=False)

# ========================= SURVEY MODELS ========================= #
class SurveyResponse(BaseSurvey):
    """ Stores name, email, and links to answers """
    __tablename__ = "survey_responses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    answers = relationship("SurveyAnswer", back_populates="response", cascade="all, delete-orphan")

class SurveyAnswer(BaseSurvey):
    """ Stores each question-answer pair for a response """
    __tablename__ = "survey_answers"
    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey("survey_responses.id", ondelete="CASCADE"))
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)

    response = relationship("SurveyResponse", back_populates="answers")

# Create Engines
waitlist_engine = create_engine(WAITLIST_DB_URL, connect_args={"check_same_thread": False})
survey_engine = create_engine(SURVEY_DB_URL, connect_args={"check_same_thread": False})

# Create Sessions
WaitlistSession = sessionmaker(autocommit=False, autoflush=False, bind=waitlist_engine)
SurveySession = sessionmaker(autocommit=False, autoflush=False, bind=survey_engine)

# Create Tables in Separate Databases
BaseWaitlist.metadata.create_all(bind=waitlist_engine)
BaseSurvey.metadata.create_all(bind=survey_engine)

# ========================= ROUTES ========================= #

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/survey')
def survey():
    return render_template("survey.html")

# ========================= WAITLIST API ========================= #
@app.route('/join-waitlist', methods=['POST'])
def join_waitlist():
    session = WaitlistSession()
    try:
        data = request.get_json()

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone_no = data.get("phone_no", "").strip()
        country = data.get("country", "Unknown").strip()
        state = data.get("state", "").strip()
        occupation = data.get("occupation", "Not specified").strip()

        # # ✅ **Check for existing email in a case-insensitive manner**
        # existing_user = session.query(Waitlist).filter(Waitlist.email.ilike(email)).first()
        # if existing_user:
        #     return jsonify({"message": "❌ Email already exists in the waitlist."}), 400

        new_entry = Waitlist(name=name, email=email, phone_no=phone_no, country=country, state=state, occupation=occupation)
        session.add(new_entry)
        session.commit()

        return jsonify({"redirect": "/thank-you-waitlist"}), 200

    # except Exception as e:
    #     session.rollback()
    #     print(f"🚨 Error: {str(e)}")  
    #     return jsonify({"message": "❌ Error joining waitlist."}), 400

    finally:
        session.close()

# Thank You Page for Waitlist
@app.route('/thank-you-waitlist')
def thank_you_waitlist():
    return render_template('thank-you-waitlist.html')  # Create this HTML file

# ========================= SURVEY API ========================= #
@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    session = SurveySession()
    try:
        data = request.form  

        name = data.get("name")  
        email = data.get("email")

        # Ensure email does not already exist
        existing_entry = session.query(SurveyResponse).filter_by(email=email).first()
        if existing_entry:
            return jsonify({"message": "❌ Survey already submitted with this email."}), 400

        # Create a new survey response entry
        new_response = SurveyResponse(name=name, email=email)
        session.add(new_response)
        session.flush()  # Get ID before committing

        # Dynamically store all question-answer pairs
        for key, value in data.items():
            if key not in ["name", "email"]:  # Ignore name & email fields
                new_answer = SurveyAnswer(response_id=new_response.id, question=key, answer=value)
                session.add(new_answer)

        session.commit()
        return redirect(url_for('thank_you'))

    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "❌ Error submitting the survey"}), 400
    finally:
        session.close()

@app.route('/thank-you')
def thank_you():
    return render_template("thankyou.html")

# Run App
if __name__ == '__main__':
    app.run(debug=True)
