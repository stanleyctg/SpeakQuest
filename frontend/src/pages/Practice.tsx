import Questions from "./components/Questions";
import Camera from "./components/Camera";
import Captions from "./components/Captions"
import "./styles/Practice.css";

export default function Practice() {
  return (
    <div className="practice-container">
      <div className="left-pane">
        <div className="question-section">
          <Questions />
        </div>
        <div className="caption-section">
          <Captions />
        </div>
      </div> 
      <div className="right-pane">
        <Camera />
      </div> 
    </div>
  );
}