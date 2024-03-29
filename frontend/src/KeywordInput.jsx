import { useState } from 'react'
import KeywordPill from './KeywordPill';

function KeywordInput({ keywords, setKeywords }) {
    const [inputValue, setInputValue] = useState('');
    const [warning, setWarning] = useState(''); 

    // Handle any change to reset any existing warnings.
    const handleInputChange = (event) => {
        const newValue = event.target.value
        setInputValue(newValue);
        setWarning(''); 
        if (newValue.includes(' ')) {
            setWarning('Multi-word keywords are not supported');
        } else {
            setWarning('');
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && inputValue && !inputValue.includes(' ')) {
            if (!keywords.includes(inputValue.toLowerCase())) {
                setKeywords([...keywords, inputValue.toLowerCase()]);
            }
            setInputValue('');
        } else if (event.key === 'Backspace' && !inputValue && keywords.length > 0) {
            // Remove the last keyword when backspace is pressed and the input is empty
            setKeywords(keywords.slice(0, -1));
        }
    };

    const handleRemoveKeyword = (keywordToRemove) => {
        setKeywords(keywords.filter(keyword => keyword !== keywordToRemove));
    };

    return (
        <div>
            {warning && <div className="bg-red-100 text-red-500 mt-2 w-fit rounded p-1">{warning}</div>} {/* Display the warning if present */}
            <div className="bg-white flex items-center p-1 border rounded mt-2 max-w-xl">
                {keywords.map(keyword => (
                    <KeywordPill key={keyword} keyword={keyword} onRemove={handleRemoveKeyword}/>
                ))}
                <input
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Enter search terms..."
                    className="bg-white flex-1 outline-none"
                />
            </div>
        </div>
    );
}

export default KeywordInput;