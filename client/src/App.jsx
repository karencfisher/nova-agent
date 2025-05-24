import { useState, useEffect, useRef } from 'react'
import { useSpeechSynthesis } from 'react-speech-kit';
import ThreeDots from 'react-loading-icons/dist/esm/components/three-dots';
import { marked } from 'marked';
import { Message } from './components/Message';
import { Prompt } from './components/Prompt';
import { Camera } from './components/Camera';
import './App.css'
import { use } from 'react';

export default function App(props) {
    const [messages, setMessages] = useState([]);
    const [talk, setTalk] = useState(false);
    const [useCamera, setUseCamera] = useState(false);
    const talkRef = useRef(talk);
    const [image, setImage] = useState(null);
    const [waiting, setWaiting] = useState(false);
    const messagesEndRef = useRef(null);
    const {cancel, voices} = useSpeechSynthesis();
    const voice = useRef(null);

    const host = 'http://192.168.1.107:5000';

    async function sendMessage(msg) {
        if (msg === "") return;
        setWaiting(true);
        const resultPromise = fetch(`${host}/message`, {
            method: "post",
            body: JSON.stringify(
                {
                    message: msg,
                    img: image
                }
            ),
            headers: {
                "Content-Type": "application/json"
            }
        });

        resultPromise.then(async (result) => {
            const response = await result.json();
            if (result.status !== 200) {
                setMessages(prevMessages => 
                    [...prevMessages, {role: "error", content: response.error}]);
            }    
        }).catch((error) => {
            setMessages(prevMessages => 
                [...prevMessages, { role: "error", content: error.message }]);
        });
    }
    
    function onsubmit(msg) {
        setMessages(prevMessages => [...prevMessages, {role: "user", content: msg}]);
        sendMessage(msg);
    }

    function sayIt(messageContent) {
        const v = voice.current
        const rate="1.5";
        let spokenContent = messageContent.replace(/\#/g, "");
        spokenContent = spokenContent.replace(/\b(?:https?:\/\/ www\.)\S+\b/g, "").trim();
        const utterance = new SpeechSynthesisUtterance(spokenContent);
        utterance.voice = v; // Set the voice
        utterance.rate = parseFloat(rate); // Set the rate if applicable
        window.speechSynthesis.speak(utterance);
    }

    useEffect(()  => {
        if (voices) {
            voice.current = voices[2];
        }
    }, [voices]);

    useEffect(() => {
        async function fetchMessages() {
            const result = await fetch(`${host}/get_messages`);
            const response = await result.json();
            setMessages(response);
        }
        fetchMessages();

        const eventSource = new EventSource(`${host}/stream`);
        eventSource.onmessage = (e) => {
            if (e.data === "") return;
            const data = JSON.parse(e.data);
            setWaiting(!data.final);
            const messageContent = data.content.replace(/\|/g, "\n");
            setMessages(prevMessages => [...prevMessages, 
                {role: "assistant", content: messageContent}]);
            if (talkRef.current) {
                sayIt(messageContent);
            }
        };
        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
        };

        return () => {
            eventSource.close();
        };
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        talkRef.current = talk;
    }, [talk])

    useEffect(() => {
        if (useCamera === false) {
            setImage(null);
        }
    }, [useCamera])

    return (
        <div className="container">
            <div className="message-container">
                {messages && messages.map((message, i) => (
                    <Message
                        key={i}
                        message={{ ...message, content: marked(message.content) }}
                    />
                ))}
                <div ref={messagesEndRef} />
            </div>
            <div className="prompt-container">
                <Prompt
                    onsubmit={onsubmit}
                    talk={talk}
                    cancel={cancel}
                />
                <div className="options">
                    <div className="speech-option">
                        <input type="checkbox" name="speech" checked={talk} 
                            onChange={e => setTalk(e.target.checked)} />
                        <label htmlFor="speech">Voice interface</label>
                    </div>
                    <div className="camera-option">
                        <input type="checkbox" name="camera" checked={useCamera} 
                            onChange={e => setUseCamera(e.target.checked)} />
                        <label htmlFor="camera">Use camera</label>
                    </div>
                </div>
            </div>
            { waiting && (
                <div className="wait-icon">
                    <ThreeDots 
                        fill="#ff0000" 
                        fillOpacity={.125}
                    />
                </div>
            )}
            { useCamera && (
                <div className="camera-container">
                    <Camera 
                        setImage={setImage}
                    />
                </div>
            )}
        </div>
    )
}

