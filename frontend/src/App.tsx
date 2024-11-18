// src/App.tsx

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App: React.FC = () => {
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');

  const handleQuestionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuestion(e.target.value);
  };

  const handleSubmit = async () => {
    if (!question) {
      alert('質問を入力してください。');
      return;
    }
    try {
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