import React, { useEffect, useState } from "react";
import Button from "./Button";
import { questions, type Question } from "../data/Question";
import "./../styles/Question.css";
import Microphone from "./Microphone";

export default function Questions() {
  const [questionIdx, setQuestionIdx] = useState<number>(0);
  const q: Question = questions[questionIdx];

  const next = () => setQuestionIdx((prev) => (prev + 1) % questions.length);

  return (
    <div className="question-container">
      <div className="question">
        <p>{q.question}</p>
      </div>
      <div className="prompts">
        <p>Key points to consider: </p>
        <ul className="prompts-list">
          {q.prompts.map((prompt, idx) => (
            <li key={idx}>{prompt}</li>
          ))}
        </ul>
      </div>
      <Microphone question={q.question} onNext={next} />{" "}
      <div className="question-button-container">
        <Button onClick={next} children="Skip Question" />{" "}
      </div>
    </div>
  );
}
