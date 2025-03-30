from flask import Flask, request, render_template
import os
import logging
import pandas as pd
import pdfplumber
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbosity if needed
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

def split_rows(df): 
    df = df.apply(lambda x: x.str.split('\n').explode())
    df = df.reset_index(drop=True) 
    return df

def clean_column_names(df):
    # Replace newlines and strip whitespace from column names
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    return df

def remove_empty_lines(df):
    # Remove rows where 'CÓD. PRODUTO' is NaN or an empty string
    df = df[df['CÓD. PRODUTO'].notna() & (df['CÓD. PRODUTO'] != '')]
    return df

def aggregate_repeated_products(df):
    df['QTDE'] = df['QTDE'].astype(int)
    df = df.groupby(['CÓD. PRODUTO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO']).agg({'QTDE': 'sum'}).reset_index()
    return df

def process_pdf(pdf_file):
    dfs = []
    required_cols = ['CÓD. PRODUTO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO', 'QTDE']
    logger.info("Opening PDF file: %s", pdf_file)
    try:
        with pdfplumber.open(pdf_file) as pdf:
            logger.info("PDF file contains %d pages", len(pdf.pages))
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    table = page.extract_table()
                    # Skip the page if no table is found or there are no data rows
                    if not table or len(table) < 2:
                        logger.debug("Page %d skipped: No table found or insufficient rows.", i)
                        continue

                    # Create a DataFrame from the table data
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = split_rows(df)
                    df = clean_column_names(df)

                    # Skip this page if the required columns are missing
                    if not all(col in df.columns for col in required_cols):
                        logger.debug("Page %d skipped: Required columns missing. Found columns: %s", i, df.columns.tolist())
                        continue

                    df = remove_empty_lines(df)
                    dfs.append(df)
                    logger.info("Page %d processed successfully.", i)
                except Exception as e:
                    logger.error("Error processing page %d: %s", i, e)
                    continue
    except Exception as e:
        logger.error("Failed to open PDF file %s: %s", pdf_file, e)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()

@app.route('/process-pdf', methods=['POST'])
def process_pdf_endpoint():
    files = request.files.getlist('files')

    if not files or all(file.filename == '' for file in files):
        logger.warning("No files selected.")
        return render_template('results.html', has_data=False, error_messages=['No files selected']), 400

    master_df = pd.DataFrame()
    errors = []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            logger.info("Processing file: %s", file.filename)
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = os.path.join(temp_dir, file.filename)
                    file.save(temp_path)
                    df = process_pdf(temp_path)
                    master_df = pd.concat([master_df, df], ignore_index=True)
                    logger.info("File %s processed successfully.", file.filename)
            except Exception as e:
                logger.error("Error processing file %s: %s", file.filename, e)
                errors.append(f'Error processing {file.filename}: {e}')

    if not master_df.empty:
        try:
            master_df = master_df[['CÓD. PRODUTO', 'DESCRIÇÃO DO PRODUTO / SERVIÇO', 'QTDE']]
        except KeyError as e:
            logger.error("Required columns not found in the data: %s", e)
            return render_template('results.html', 
                                has_data=False, 
                                error_messages=['Error: Required columns not found in the data.']), 400
        
        # If QTDE contains extra data (e.g., commas), take the first part
        master_df['QTDE'] = master_df['QTDE'].str.split(',').str[0]
        master_df = aggregate_repeated_products(master_df)
        master_df = master_df.sort_values(by='DESCRIÇÃO DO PRODUTO / SERVIÇO')
        table_html = master_df.to_html(classes="table-auto w-full", index=False, header=True)
        table_html = table_html.replace('<th>', '<th style="text-align: left;">')
        
        return render_template('results.html',
                             has_data=True,
                             table_html=table_html,
                             error_messages=errors if errors else None)
    else:
        logger.warning("No data to display after processing files.")
        return render_template('results.html',
                             has_data=False,
                             error_messages=errors if errors else ['No data to display'])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
