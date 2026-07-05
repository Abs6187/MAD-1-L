import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        df = pd.read_csv('./data.csv', skipinitialspace=True)
        id_type = request.form.get('ID')
        id_value = request.form.get('id_value')

        if id_type == 'student_id' and id_value:
            return student_data(df, int(id_value))
        elif id_type == 'course_id' and id_value:
            return course_data(df, int(id_value))
        else:
            return render_template('error.html')

def export_plot(marks):
    lower_limit = (marks['Marks'].min() // 10) * 10
    freq = marks['Marks'].value_counts().sort_index()
    x = freq.index
    plt.figure(figsize=(10, 6))
    plt.bar(x, freq.values, width=1, align='center')
    plt.xlim(lower_limit, 100)
    plt.xticks(range(lower_limit, 101, 10))
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('./static/bar-chart.png', dpi=300, bbox_inches='tight')
    plt.close()

def student_data(df, sid):
    courses = df.loc[df['Student id'] == sid]

    if len(courses) == 0:
        return render_template('error.html')

    total = courses['Marks'].sum()
    return render_template('student_data.html', courses=courses.to_dict(orient='records'), total=total)

def course_data(df, cid):
    marks = df.loc[df['Course id'] == cid]

    if len(marks) == 0:
        return render_template('error.html')

    avg = marks['Marks'].mean()
    max_marks = marks['Marks'].max()
    export_plot(marks)
    return render_template('course_data.html', avg=avg, max_marks=max_marks)

if __name__ == '__main__':
    app.run(debug=False, port=5000) 

# New route to compare both CSV files
@app.route('/compare')
def compare():
    df1 = pd.read_csv('data.csv', skipinitialspace=True)
    df2 = pd.read_csv('data (1).csv', skipinitialspace=True)
    # Perform outer merge to find differences
    diff = df1.merge(df2, on=['Student id', 'Course id', 'Marks'], how='outer', indicator=True)
    diffs = diff[diff['_merge'] != 'both']
    if diffs.empty:
        return render_template('identical.html')
    else:
        # Convert differences to list of dicts for rendering
        diff_records = diffs.to_dict(orient='records')
        return render_template('diff.html', differences=diff_records)
