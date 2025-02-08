function KeywordPill({keyword, onRemove}) {
    return (
      <div className="inline-flex items-center border border-stone-600 bg-stone-100 text-stone-500 rounded px-1 py-0.5 mr-2 text-sm">
        {keyword}
        <button
          type="button"
          onClick={() => onRemove(keyword)}
          className="ml-2 text-stone-500 hover:text-stone-800 rounded-full"
        >
          &times;
        </button>
      </div>
    );
  }

export default KeywordPill;