from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import docx

app = Flask(__name__)
CORS(app)

# アップロードされたファイルを保存するディレクトリ
UPLOAD_FOLDER = 'uploaded_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# サポートされているファイルの拡張子
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# OpenAI APIキーの確認
if 'OPENAI_API_KEY' not in os.environ:
    raise Exception("OpenAI APIキーが設定されていません。")

# グローバル変数としてベクトルストアを初期化
vectorstore = None
embeddings = OpenAIEmbeddings()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_file(file_path):
    """ファイルの内容をテキストとして読み込む"""
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == 'pdf':
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif ext == 'docx':
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    else:
        return ''

@app.route('/api/upload', methods=['POST'])
def upload_file():
    global vectorstore
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません。'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません。'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # ファイルからテキストを読み込む
        document = load_file(file_path)
        if not document:
            return jsonify({'error': 'ファイルの読み込みに失敗しました。'}), 500

        # ベクトルストアを作成
        vectorstore = FAISS.from_texts([document], embeddings)
        return jsonify({'message': 'ファイルがアップロードされ、処理されました。'})
    else:
        return jsonify({'error': '許可されていないファイル形式です。'}), 400

@app.route('/api/ask', methods=['POST'])
def ask():
    global vectorstore
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': '質問が必要です。'}), 400
    if vectorstore is None:
        return jsonify({'error': 'ドキュメントがアップロードされていません。'}), 400
    try:
        # RetrievalQAチェーンの作成
        llm = OpenAI()
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        answer = qa.run(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
