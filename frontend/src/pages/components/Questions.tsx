import React, { useState } from 'react';
import Button from './Button';

const placeholderQuestions: string[] = [
    "Tell me about yourself.",
    "Why are you interested in this role?",
    "What are your strengths?",
    "Describe a challenge you faced and how you overcame it.",
    "Where do you see yourself in 5 years?",
]as const;

export default function Questions() {
    const [questionIdx, setQuestionIdx] = useState<number>(0);

    return(
        <div>
            <h1>Questions</h1>
            <p>{placeholderQuestions[questionIdx]}</p>
            <Button
                onClick={() => setQuestionIdx((prev) => (prev + 1) % placeholderQuestions.length)}
                children="Next Question"
            />


        </div>
    )
}