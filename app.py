# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import os

app = Flask(__name__)
CORS(app)

# OpenAI APIキーの設定
if 'OPENAI_API_KEY' not in os.environ:
    os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY'  # 安全のため環境変数から取得することを推奨

# ドキュメントデータの準備
documents = [
    "今日はとても良い天気です。",
    "明日は雨が降る予報です。",
    "週末は旅行に行く予定です。",
    "Pythonは人気のあるプログラミング言語です。",
    "機械学習はデータ分析の一部です。"
]

# Embeddingsとベクトルストアの作成
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(documents, embeddings)

# RetrievalQAチェーンの作成
llm = OpenAI()
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# エンドポイントの定義
@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': '質問が必要です。'}), 400
    try:
        answer = qa.run(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

