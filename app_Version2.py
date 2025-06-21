from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from models import init_db, get_db, create_form_schema, get_all_forms, get_form_schema, save_form_submission, get_form_submissions
import io
import csv

app = Flask(__name__)

@app.before_first_request
def initialize():
    init_db()

@app.route("/")
def index():
    forms = get_all_forms()
    return render_template("index.html", forms=forms)

@app.route("/create_form", methods=["GET", "POST"])
def create_form():
    if request.method == "POST":
        form_name = request.form["form_name"]
        fields = request.form.getlist("fields[]")
        create_form_schema(form_name, fields)
        return redirect(url_for("index"))
    return render_template("create_form.html")

@app.route("/form/<int:form_id>", methods=["GET", "POST"])
def show_form(form_id):
    form = get_form_schema(form_id)
    if not form:
        return "Form not found", 404
    if request.method == "POST":
        # Save submission
        submission = {f: request.form.get(f, "") for f in form['fields']}
        save_form_submission(form_id, submission)
        return redirect(url_for('show_form', form_id=form_id))
    return render_template("form.html", form=form)

@app.route("/form/<int:form_id>/export")
def export_form(form_id):
    form = get_form_schema(form_id)
    submissions = get_form_submissions(form_id)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=form['fields'])
    writer.writeheader()
    for submission in submissions:
        writer.writerow(submission)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{form['name']}_submissions.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)