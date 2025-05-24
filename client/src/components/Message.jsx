import { marked } from 'marked';
import './Message.css';

export function Message(props) {
    const {message} = props;

    return (
        <div 
            className={message.role} 
            dangerouslySetInnerHTML={{ __html: marked(message.content) }} 
        />
    )
}