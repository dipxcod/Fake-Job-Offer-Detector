from flask import Flask, render_template, request
from flask import send_file
from reportlab.pdfgen import canvas
from datetime import datetime
import os

app = Flask(__name__)
last_result = {}

scam_words = [
    "registration fee",
    "processing fee",
    "pay now",
    "urgent",
    "security deposit",
    "offer letter fee",
    "training fee",
    "guaranteed job",
    "limited seats",
    "refundable fee",
    "immediate joining",
    "selected immediately",
    "click here",
    "confirm your seat",
    "payment required"
]
trusted_domains = [
    "ibm.com",
    "google.com",
    "microsoft.com",
    "amazon.com",
    "apple.com",
    "infosys.com",
    "tcs.com",
    "wipro.com",
    "accenture.com"
]

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/check', methods=['POST'])
def check():

    text = request.form['jobtext'].lower()
    email = request.form['email'].lower()

    score = 0
    reasons = []

    for word in scam_words:
        if word in text:
            score += 15
            reasons.append(word)
    # Limit score to 100%
    if score > 100:
        score = 100

    if score >= 70:
        status = "High Risk Scam"
        color = "danger"
    elif score >= 40:
        status = "Suspicious"
        color = "warning"
    else:
        status = "Looks Safe"
        color = "success"

    if status == "Looks Safe":

        summary = "No major scam indicators were detected. Continue to verify the company through official channels."

    elif status == "Suspicious":

        summary = "Several suspicious indicators were detected. Additional verification is recommended before proceeding."

    else:

        summary = "Multiple high-risk scam indicators were detected. This offer should be treated as potentially fraudulent."
        
    email_status = "Suspicious"

    for domain in trusted_domains:

        if email.endswith(domain):

            email_status = "Trusted"

            break
    global last_result

    confidence = min(score + 10, 100)
    # Dynamic Security Recommendations

    if status == "Looks Safe":

        recommendations = [
            "Verify the company website before proceeding.",
            "Attend interviews only through official communication.",
            "Do not share confidential information unnecessarily."
        ]

    elif status == "Suspicious":

        recommendations = [
            "Verify the recruiter's email domain.",
            "Contact the company through its official website.",
            "Do not share Aadhaar, PAN or bank details.",
            "Do not pay any registration or processing fee."
        ]

    else:

        recommendations = [
            "This job offer has a high probability of being fraudulent.",
            "Never pay registration, training or processing fees.",
            "Do not share OTP, passwords or banking information.",
            "Block the sender and report the scam if possible.",
            "Verify the company using official contact details only."
        ]
    

    last_result = {
        "email": email,
        "email_status": email_status,
        "score": score,
        "status": status,
        "reasons": reasons,
        "confidence": confidence,
        "recommendations": recommendations,
        "summary": summary
        
    }

    

    return render_template(
        "result.html",
        score=score,
        status=status,
        reasons=reasons,
        color=color,
        email=email,
        email_status=email_status
    )
@app.route('/download')
def download():
    filename = "Security_Report.pdf"
    c = canvas.Canvas(filename)
    y = 800
    c.setFont("Helvetica-Bold",20)
    c.drawString(130,y,"Security Analysis Report")
    y -= 40
    c.setFont("Helvetica",12)
    c.drawString(50,y,"Analysis Time : " + datetime.now().strftime("%d-%m-%Y %I:%M %p"))
    y -= 30
    c.drawString(50,y,"Recruiter Email : " + last_result["email"])
    y -= 25
    c.drawString(50,y,"Email Status : " + last_result["email_status"])
    y -= 35
    c.drawString(50,y,"Risk Score : " + str(last_result["score"]) + "%")
    y -= 25
    c.drawString(50,y,"Risk Level : " + last_result["status"])
    y -= 25
    c.drawString(50,y,"Detection Confidence : " + str(last_result["confidence"]) + "%")
    y -= 40
    c.setFont("Helvetica-Bold",14)
    c.drawString(50,y,"Indicators Found")
    y -= 25
    c.setFont("Helvetica",12)
    if len(last_result["reasons"]) == 0:
        c.drawString(60,y,"No suspicious indicators detected.")
    else:
        for reason in last_result["reasons"]:
            c.drawString(60,y,"• " + reason)
            y -= 20
            
    y -= 20
    c.setFont("Helvetica-Bold",14)
    c.drawString(50,y,"Analysis Summary")
    y -= 25
    c.setFont("Helvetica",12)
    c.drawString(60,y,last_result["summary"])

    
    y -= 20
    c.setFont("Helvetica-Bold",14)
    c.drawString(50,y,"Security Recommendations")
    y -= 25
    c.setFont("Helvetica",12)

    for rec in last_result["recommendations"]:
        c.drawString(60,y,"• " + rec)
        y -= 20
    y -= 20
    c.drawString(50,y,"Generated by Fake Job Offer Detector")
    y -= 20
    c.drawString(50,y,"Developed by Dipak Varude")
    c.save()
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
