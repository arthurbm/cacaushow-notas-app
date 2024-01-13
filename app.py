from flask import Flask, request, render_template_string, render_template
import os
import pandas as pd
import pdfplumber
import tempfile

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def split_rows(df): 
    df = df.apply(lambda x: x.str.split('\n').explode())
    df = df.reset_index(drop=True) 
    return df

def clean_column_names(df):
    df.columns = df.columns.str.replace('\n', ' ')
    return df

def remove_empty_lines(df):
    df = df[df['CÓD. PRODUTO'].notna() & (df['CÓD. PRODUTO'] != '')]
    return df

def aggregate_repeated_products(df):
    df['QTDE'] = df['QTDE'].astype(int)
    df = df.groupby(['CÓD. PRODUTO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO']).agg({'QTDE': 'sum'}).reset_index()
    return df

def process_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        table = pdf.pages[0].extract_table()
    df = pd.DataFrame(table[1:], columns=table[0])
    df = split_rows(df)
    df = clean_column_names(df)
    df = remove_empty_lines(df)
    return df

@app.route('/process-pdf', methods=['POST'])
def process_pdf_endpoint():
    files = request.files.getlist('files')
    print('files', request.files)

    if not files or all(file.filename == '' for file in files):
        return render_template_string('<div class="text-red-500">No files selected</div>'), 400

    master_df = pd.DataFrame()
    errors = []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = os.path.join(temp_dir, file.filename)
                    file.save(temp_path)
                    df = process_pdf(temp_path)
                    master_df = pd.concat([master_df, df], ignore_index=True)
            except Exception as e:
                errors.append(f'Error processing {file.filename}: {e}')

    if not master_df.empty:
        master_df = master_df[['CÓD. PRODUTO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO', 'QTDE']]
        master_df['QTDE'] = master_df['QTDE'].str.split(',').str[0]
        master_df = aggregate_repeated_products(master_df)
        master_df = master_df.sort_values(by='DESCRIÇÃO DO PRODUTO / SERVIÇO')
        result_html = master_df.to_html(classes="table-auto w-full", index=False, header=True)
        result_html = result_html.replace('<th>', '<th style="text-align: left;">')
    else:
        result_html = '<div class="text-red-500">No data to display</div>'

    error_html = '<br>'.join(errors)
    return render_template_string(f'{result_html}<div class="text-red-500">{error_html}</div>')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
