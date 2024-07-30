from flask import Flask, request, jsonify, render_template, redirect, url_for
from dotenv import load_dotenv
from flask_cors import CORS
import os
import re
import random
from textblob import TextBlob
import google.generativeai as genai
import fitz  # PyMuPDF

app = Flask(__name__)
load_dotenv()
CORS(app, origins=["*"])

genai.configure(api_key=os.getenv("gemini_api_key"))

# Define DSA topics
topic = {
    "Arrays": [
        "Dynamic Programming (DP) problems related to arrays.",
        "Sorting algorithms for arrays.",
        "Search algorithms for arrays."
    ],
    "Linked Lists": [
        "Dynamic Programming (DP) problems related to linked lists.",
        "Insertion and deletion operations in linked lists.",
        "Cyclic detection and removal in linked lists."
    ],
    "Stacks and Queues": [
        "Implementing stacks and queues using arrays or linked lists.",
        "Applications of stacks and queues in algorithm design.",
        "Optimizing stack and queue operations for efficiency."
    ],
    "Trees": [
        "Dynamic Programming (DP) problems related to trees.",
        "Traversal algorithms for trees (e.g., inorder, preorder, postorder).",
        "Balancing techniques for binary search trees."
    ]
}

rubric = {
    "Excellent": {
        "min_score": 90,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Good": {
        "min_score": 75,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Satisfactory": {
        "min_score": 55,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Fair": {
        "min_score": 40,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    },
    "Poor": {
        "min_score": 0,
        "criteria": {
            "Accuracy": {"weight": 0.14},
            "Completeness": {"weight": 0.175},
            "Relevance": {"weight": 0.08},
            "Clarity": {"weight": 0.175},
            "Depth": {"weight": 0.09},
            "Organization": {"weight": 0.1},
            "Use of Evidence": {"weight": 0.09},
            "Grammar and Spelling": {"weight": 0.1},
            "Sentiment": {"weight": 0.075}
        }
    }
}

def post_process_text(text):
    cleaned_text = text.replace("**", "")
    return cleaned_text

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def generate_custom_tech_questions(skills):
    prompt = f"""Can you give me 10 interview questions for freshers based on the mandatory skills mentioned in the job description as follows: {skills}.

    **I need the response in a strictly numbered and bulleted format.**

    Question 1:       (\n\n\n\n\n)
    Question 2:       (\n\n\n\n\n)
    Question 3:       (\n\n\n\n\n)
    Question 4:       (\n\n\n\n\n)
    
    """

    response = genai.GenerativeModel('gemini-pro').generate_content(prompt)
    return post_process_text(response.text)

def generate_custom_non_tech_questions(resume_text, job_description_text):
    prompt = (f"""Imagine you are conducting an interview with a candidate who has submitted a resume highlighting their 
              work experience and projects relevant to the position. Craft a set of questions that delve into their 
              past experiences and assess their technical skills based on the requirements outlined in the job 
              description. Work Experience: Review the candidate's work experience as outlined in their resume. 
              Craft questions that explore specific accomplishments, challenges faced, and roles undertaken in their 
              previous positions. Project Experience: Analyze the projects listed on the candidate's resume. Develop 
              questions that probe into the methodologies employed, the candidate's contributions, problem-solving 
              strategies, and lessons learned from these projects. Technical Skills: Referencing the technical 
              skills mentioned in the job description, devise questions to evaluate the candidate's proficiency in 
              these areas. These questions should assess not only theoretical knowledge but also practical 
              application and problem-solving abilities. Integration of Experience and Skills: Formulate questions 
              that require the candidate to integrate their past work experiences and technical skills. This could 
              involve hypothetical scenarios or real-world challenges relevant to the role they are applying for.
              Here is the resume: \n{resume_text} \n\n Here is the job description: \n{job_description_text}
              I need the response in a structure as:
              
              Question: 1   \n\n\n\n\n
              Question: 2   \n\n\n\n\n\n
              ...
              """)
    response = genai.GenerativeModel('gemini-pro').generate_content(prompt)
    return post_process_text(response.text)

def generate_dsa_questions():
    prompt = (f"""**Topic:** {topic}

    **Instructions:**
    - This question is commonly encountered in programming competitions and assessments.
    - The problem statement should revolve around a concept or problem related to {topic}.
    - Provide a concise description of the problem or concept, ensuring clarity and accuracy.
    - Include examples or test cases to illustrate the problem statement effectively.
    - Ensure proper formatting and punctuation for clear presentation.

    Write a question that adheres to the provided instructions.   \n 
    Test Cases:   \n
    Input 1:[]    \n
    Output 1:[]   \n
    ......
    """)
    response = genai.GenerativeModel('gemini-pro').generate_content(prompt)
    return post_process_text(response.text)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.files['job_description']
        resume = request.files['resume']
        skills = request.form['skills']

        job_description_text = extract_text_from_pdf(job_description)
        resume_text = extract_text_from_pdf(resume)

        # Store the extracted data in the session or pass it directly
        return render_template('questions.html', tech_questions='', non_tech_questions='', dsa_questions='')

    return render_template('index.html')

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    skills = request.form.get('skills')
    resume_text = extract_text_from_pdf(request.files['resume'])
    job_description_text = extract_text_from_pdf(request.files['job_description'])

    tech_questions = generate_custom_tech_questions(skills)
    non_tech_questions = generate_custom_non_tech_questions(resume_text, job_description_text)
    dsa_questions = generate_dsa_questions()

    return render_template('questions.html', tech_questions=tech_questions, non_tech_questions=non_tech_questions,
                           dsa_questions=dsa_questions)

@app.route('/dsa_questions', methods=['GET'])
def dsa_questions():
    return render_template('dsa_questions.html', dsa_questions=generate_dsa_questions())

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    prompt = f"""
Imagine you are conducting a professional interview and your task is to evaluate the candidate's response to a specific question. The question posed to the candidate is: "{question}". 

In this evaluation, please analyze the following aspects of the candidate's response: 
- Accuracy: Does the response accurately address the question? \n
- Completeness: Does the response provide a thorough and detailed answer? \n
- Relevance: Is the response relevant to the question and the topic at hand? \n
- Clarity: Is the response clear and easy to understand? \n
- Depth: Does the response demonstrate a deep understanding of the subject matter? \n
- Organization: Is the response well-organized and logically structured? \n
- Use of Evidence: Does the response provide evidence or examples to support the claims made? \n
- Grammar and Spelling: Is the response free from grammatical and spelling errors? \n
- Sentiment: Analyze the overall sentiment of the response, indicating whether it is positive, negative, or neutral.\n

Here's the candidate's response: "{answer}". 

Provide a detailed evaluation of the response, considering each of the aspects mentioned above. Please ensure that the evaluation is thorough and objective, highlighting both strengths and areas for improvement.
    """

    response = genai.GenerativeModel('gemini-pro').generate_content(prompt)
    evaluation_text = response.text.strip()

    evaluation_criteria = {
        "Accuracy": 10,
        "Completeness": 8,
        "Relevance": 7,
        "Clarity": 9,
        "Depth": 6,
        "Organization": 7,
        "Use of Evidence": 8,
        "Grammar and Spelling": 9,
        "Sentiment": 7
    }

    evaluation_result = {}
    for criterion, weight in evaluation_criteria.items():
        pattern = rf"{criterion}: (\d+)"
        match = re.search(pattern, evaluation_text)
        if match:
            score = int(match.group(1))
            evaluation_result[criterion] = score * weight / 10

    total_score = sum(evaluation_result.values())

    # Assign grade based on total score
    if total_score >= 90:
        grade = "Excellent"
    elif total_score >= 75:
        grade = "Good"
    elif total_score >= 55:
        grade = "Satisfactory"
    elif total_score >= 40:
        grade = "Fair"
    else:
        grade = "Poor"

    evaluation_data = {
        "score": total_score,
        "grade": grade,
        "evaluation_text": evaluation_text,
        "evaluation_result": evaluation_result
    }

    return jsonify(evaluation_data)

@app.route('/evaluate', methods=['GET'])
def evaluate_page():
    return render_template('evaluate.html')

if __name__ == '__main__':
    app.run(debug=True)
