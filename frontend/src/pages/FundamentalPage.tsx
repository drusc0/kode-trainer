import { Link, useParams } from "react-router-dom";
import Markdown from "../components/Markdown";
import { FUNDAMENTALS, fundamentalBody } from "../content/design";

export default function FundamentalPage() {
  const { slug = "" } = useParams();
  const idx = FUNDAMENTALS.findIndex((f) => f.slug === slug);
  const topic = FUNDAMENTALS[idx];

  if (!topic)
    return (
      <main className="page">
        <h1>Unknown topic</h1>
        <Link to="/design">Back to system design</Link>
      </main>
    );
  const prev = FUNDAMENTALS[idx - 1];
  const next = FUNDAMENTALS[idx + 1];

  return (
    <main className="page pattern-page">
      <Link to="/design" className="back">
        ← System design
      </Link>
      <p className="eyebrow">
        Fundamental {idx + 1} of {FUNDAMENTALS.length}
      </p>
      <h1>{topic.title}</h1>
      <p className="lede">{topic.summary}</p>
      <article>
        <Markdown>{fundamentalBody(slug)}</Markdown>
      </article>
      <nav className="pager">
        {prev ? <Link to={`/design/learn/${prev.slug}`}>← {prev.title}</Link> : <span />}
        {next ? <Link to={`/design/learn/${next.slug}`}>{next.title} →</Link> : <span />}
      </nav>
    </main>
  );
}
