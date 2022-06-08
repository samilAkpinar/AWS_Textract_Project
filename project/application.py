import os
import boto3
from flask import render_template, request, session, redirect, url_for, Flask

application = Flask(__name__)

ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
AWS_REGION = ''

# Creating Session With Boto3.
_session = boto3.Session(aws_access_key_id=ACCESS_KEY_ID,
                         aws_secret_access_key=ACCESS_SECRET_KEY,
                         region_name=AWS_REGION
                         )

s3 = _session.resource('s3')

# Creating textract client from boto3
textract_client = boto3.client('textract',
                               aws_access_key_id=ACCESS_KEY_ID,
                               aws_secret_access_key=ACCESS_SECRET_KEY,
                               region_name=AWS_REGION)


@application.route('/')
def home():
    return render_template('home.html')


@application.route('/uploadConvert', methods=['post'])
def uploadConvert():
    if request.method == 'POST':
        file_name = request.form['image']
        if file_name == "":
            return render_template('home.html')

        try:
            result = s3.Bucket('mybucketformycloudproject').upload_file(os.path.abspath(r"files/" + file_name),
                                                                    r"files/" + file_name)

            response = textract_client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': 'mybucketformycloudproject',
                        'Name': r"files/" + file_name
                    }
                }
            )
        except:
            return render_template('home.html')
        tempstr = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                tempstr += item["Text"]

        object = s3.Object('mybucketformycloudproject', r'convertedFiles/' + file_name + '_ilovetextract.txt')
        object.put(Body=tempstr)

    link = r"https://mybucketformycloudproject.s3.amazonaws.com/convertedFiles/" + file_name + r"_ilovetextract.txt"
    return render_template('downloadPage.html', link=link)




if __name__ == "__main__":
    application.run(debug=True, host='localhost')
