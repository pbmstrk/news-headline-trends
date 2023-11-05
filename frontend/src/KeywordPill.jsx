function KeywordPill({keyword, onRemove}) {
    return <div className="flex items-center space-x-2 border border-blue-400 text-blue-500 rounded bg-blue-100 px-1 py-0.5 mr-2 text-sm">
        {keyword}
        <button
        type="button"
        onClick={() => onRemove(keyword)}
        className="text-blue-500 hover:text-blue-800 rounded-full ml-2">
            &times;
        </button>
    </div>
}

export default KeywordPill;