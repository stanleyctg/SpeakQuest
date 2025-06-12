import React, { useEffect, useState } from "react";
import Button from "./Button";
import { questions, type Question } from "../data/Question";

export default function Questions() {
  const [questionIdx, setQuestionIdx] = useState<number>(0);
  const q: Question = questions[questionIdx];

  const next = () => setQuestionIdx((prev) => (prev + 1) % questions.length);

  return (
    <div>
      <div>
        <h1>Question</h1>
        <p>{q.question}</p>
      </div>

      <div>
        <h2>Key points to consider</h2>
        <ul>
          {q.prompts.map((prompt, idx) => (
            <li key={idx}>{prompt}</li>
          ))}
        </ul>
      </div>

      <Button onClick={next} children="Next Question" />
    </div>
  );
}
