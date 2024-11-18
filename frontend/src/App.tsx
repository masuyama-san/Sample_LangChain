import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App: React.FC = () => {
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleQuestionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(e.target.value);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!question) {
      alert('質問を入力してください。');
      return;
    }
    if (!selectedFile) {
      alert('ドキュメントファイルを選択してください。');
      return;
    }

    try {
      // ファイルをバックエンドにアップロード
      const formData = new FormData();
      formData.append('file', selectedFile);

      await axios.post('http://127.0.0.1:5000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 質問を送信して回答を取得
      const response = await axios.post('http://127.0.0.1:5000/api/ask', {
        question: question,
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
      alert('エラーが発生しました。');
    }
  };

  return (
    <div style={{ padding: '50px' }}>
      <h1>ドキュメント検索エージェント</h1>
      <input type="file" accept=".txt,.pdf,.docx" onChange={handleFileChange} />
      <br />
      <textarea
        rows={4}
        cols={50}
        placeholder="質問を入力してください..."
        value={question}
        onChange={handleQuestionChange}
      />
      <br />
      <button onClick={handleSubmit}>送信</button>
      <h2>回答:</h2>
      <p>{answer}</p>
    </div>
  );
};

export default App;
