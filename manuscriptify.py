from flask import (
    Flask,
    Response,
    flash,
    render_template,
    request,
)
import os
import pypandoc
import shutil
import subprocess
import tempfile


application = Flask(__name__)
application.secret_key = 'asdf'

@application.route('/', methods=['POST', 'GET'])
def manuscriptify():
    if request.method == 'POST':
        # process and download file
        if 'input' not in request.files:
            flash('No file uploaded')
            return render_template('front.html')
        f = request.files['input']
        if f.filename == '':
            flash('No file uploaded')
            return render_template('front.html')
        with tempfile.NamedTemporaryFile(suffix='.{}'.format(
                f.filename.split('.')[-1])) as temp:
            temp.write(f.read())
            temp.flush()
            contents = pypandoc.convert_file(temp.name, 'latex')
        latex = render_template('manuscript.tex',
                                contents=contents,
                                title=request.form.get('title', 'untitled'),
                                author=request.form.get('author', 'Anon.'))
        tempdir = tempfile.mkdtemp()
        with open(os.path.join(tempdir, 'manuscript.tex'), 'w') as f:
            f.write(latex)
        subprocess.call([
            'pdflatex',
            '-output-directory',
            tempdir,
            os.path.join(tempdir, 'manuscript.tex')
        ])
        with open(os.path.join(tempdir, 'manuscript.pdf'), 'rb') as f:
            result = f.read()
        shutil.rmtree(tempdir, True)
        return Response(result, mimetype='application/pdf')
    try:
        input_formats = subprocess.check_output(
            ['pandoc', '--list-input-formats'])
        input_formats = input_formats.decode()
    except:
        input_formats = '''
        I can't tell for sure, pandoc isn't new enough.  It's usually this:
        Input formats:  commonmark, docbook, docx, epub, haddock, html, json*, latex,
                markdown, markdown_github, markdown_mmd, markdown_phpextra,
                markdown_strict, mediawiki, native, odt, opml, org, rst, t2t,
                textile, twiki
                [ *only Pandoc's JSON version of native AST]
        '''
    return render_template('front.html', input_formats=input_formats.strip())


if __name__ == '__main__':
    application.run()
