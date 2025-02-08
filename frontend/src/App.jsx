import KeywordGraphPanel from './KeywordGraphTablePanel'
import nytLogo from './assets/poweredby_nytimes_150a.png'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faGithub } from '@fortawesome/free-brands-svg-icons'


function Footer() {
  let repoLink = "https://github.com/pbmstrk/news-headline-trends";

  return (
    <div className="flex justify-between items-center my-4 px-10">
      <a href="https://developer.nytimes.com" target="_blank" rel="noopener noreferrer">
        <img src={nytLogo} alt="NYT logo" className="h-10 w-auto" />
      </a>
      <a
        href={repoLink}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-500"
      >
        <FontAwesomeIcon icon={faGithub} /> pbmstrk
      </a>
    </div>
  );
}

function Title() {
  return (
    <div className="max-w-3xl mx-auto mt-8 text-center">
      <h2 className="text-4xl font-bold mb-2">
        What is <em className="font-serif not-italic underline">The New York Times</em> writing about?
      </h2>
      <p className="text-gray-600 text-md">
        Use the input box below to view the occurences of different words over
        the past 25 years. By clicking on a trace in the graph, headlines
        containing the given word during that time period can be sampled.
      </p>
    </div>
  );
}

function App() {
  return (
    <div className="bg-white flex flex-col text-black min-h-screen">
      <Title />
      <div className="flex-grow">
        <KeywordGraphPanel />
      </div>

      <Footer />
    </div>

  )
}


export default App;