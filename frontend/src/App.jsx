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

function About() {
  return (
    <div>
      <h2 className='text-3xl font-semibold mb-2'>What is the NYT writing about?</h2>
      <p>Use the input box below to view the occurences of different words over the past 25 years. By clicking on a trace in the graph, headlines containing the given word during that timeperiod can be sampled.</p>
    </div>
  )
}

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <div className="bg-gray-200 px-8 py-4">
        <h1 className="text-4xl font-bold">NYT: News Trends</h1>
      </div>

      <div className="flex-grow px-8 mt-4">
        <About />
        <KeywordGraphPanel />
      </div>

      <Footer />
    </div>

  )
}


export default App;