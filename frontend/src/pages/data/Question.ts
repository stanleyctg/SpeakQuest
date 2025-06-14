export interface Question {
  question: string;
  prompts: string[];
}

export const questions: Question[] = [
  {
    question: "Tell me about yourself.",
    prompts: [
      "Brief overview of your career path so far",
      "Hard + soft skills you’ve developed",
      "One or two standout achievements",
      "Why this background makes you a great fit",
    ],
  },
  {
    question: "Why are you interested in this role?",
    prompts: [
      "What you admire about the company’s mission or product",
      "How the role aligns with your career goals",
      "Values or culture traits that resonate with you",
      "Specific challenges you’re excited to tackle",
    ],
  },

  {
    question: "What are your greatest strengths?",
    prompts: [
      "Key skills or traits that set you apart",
      "How these strengths have helped in past roles",
      "Examples of when you’ve used these strengths",
      "How they relate to the role you’re applying for",
    ],
  },
  {
    question: "What is your biggest weakness?",
    prompts: [
      "A real weakness, not a disguised strength",
      "Steps you’ve taken to improve in this area",
      "How you manage this weakness in a work context",
      "Why this weakness won’t impact your performance in the role",
    ],
  },
  {
    question: "Describe a time you overcame a difficult challenge.",
    prompts: [
      "Situation: context & goal",
      "Obstacle: unexpected roadblock",
      "Action: concrete steps you took",
      "Result: measurable impact",
    ],
  },
  {
    question: "Where do you see yourself in five years?",
    prompts: [
      "How this role fits your growth plan",
      "New skills or leadership roles you want to take on",
      "Your vision of contributing at higher levels",
      "Commitment to evolving with the company",
    ],
  },
];
