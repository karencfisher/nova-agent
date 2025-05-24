import { useState, useEffect, useRef } from "react";
import { useSpeechRecognition } from "react-speech-kit";
import './Prompt.css';

export function Prompt(props) {
    const [prompt, setPrompt] = useState("");
    const {listen, listening, stop} = useSpeechRecognition({
        continuous: true,    
        onResult: (result) => {
            setPrompt(result);
        },
        onEnd: () => {
            if (prompt.length > 0) {
                send();
            }
        }
    });
    const {onsubmit, talk, cancel} = props;
    const talkRef = useRef(talk);

    function send() {
        if (prompt === "") return;
        onsubmit(prompt);
        setPrompt("");
    }
    
    function handleKeyDown(e) {
        if (talkRef.current && e.key === "Alt") {
            e.preventDefault();
            listen();
        }
    }

    function handleKeyUp(e) {
        if (talkRef.current && e.key === "Alt") {
            stop();
        }
    }

    useEffect(() => {
        window.addEventListener("keydown", handleKeyDown);
        window.addEventListener("keyup", handleKeyUp);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
            window.removeEventListener("keyup", handleKeyUp);
        }
    }, [])

    useEffect(() => {
        talkRef.current = talk;
        cancel();
    }, [talk])

    useEffect(() => {
        cancel();
    }, [prompt]);

    return (
        <div className="prompt" method="post">
            <textarea id="prompt" name="prompt" rows="5" value={prompt}
                onChange={(e) => setPrompt(e.target.value)} />
            <div className="buttons">
                <button onClick={send}>Send</button>
                {talk ? (
                    <button 
                        onMouseDown={listen} 
                        onMouseUp={stop}
                        data-lit={listening ? "true": "false"}
                    >
                        Talk
                    </button>
                ) : (
                    <></>
                )}
            </div>
        </div>
    )
}
