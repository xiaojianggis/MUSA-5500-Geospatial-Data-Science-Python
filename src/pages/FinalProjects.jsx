import React from "react";
import "./FinalProject.css";


const requirements = [
  "Data is collected through a means more sophisticated than downloading (e.g., scraping, API).",
  "It combines data collected from 3 or more different sources.",
  "The analysis of the data is reasonably complex (geospatial joins/operations, data shaping, etc.).",
  "Use OSMnx or pandana to analyze street networks.",
  "Use scikit-learn to perform a clustering analysis.",
  "Analyze raster data using rasterio, rasterstats, or xarray.",
  "Perform a machine learning analysis with scikit-learn.",
  "Include a deployed Panel dashboard.",
  "Include multiple interactive visualizations with significant interactivity (cross-filtering, widgets, etc.).",
];

const examples = [
  {
    title: "Addressing Disparities Across Pennsylvania Counties: A Data-Driven Approach to Equitable Resource Allocation",
    blurb:
      "By examining demographic, economic, and environmental data, the goal is to uncover patterns and clusters of counties that highlight disparities and areas of need. ",
    href: "https://ryanswett01.github.io/final_macy_ryan/",
  },
  {
    title: "Fair Pricing and Quality Optimization in Amsterdam’s Airbnb Market",
    blurb:
      "Addressing how multidimensional data can assist renters in determining fair price ranges, encourage hosts to price reasonably, and help the government manage rental quality without bias presents an intriguing research topic.",
    href: "https://shihangheisenberg.github.io/xx/",
  },

  {
    title: "Bus Lane and Transit Signal Prioritization in Philadelphia",
    blurb:
      "We specifically look at how a data-driven approach, leveraging ridership patterns, bus operational performance, and demographic indicators, can be utilized to recommend strategic interventions that not only improve transit service reliability but also address mobility challenges for underserved communities.",
    href: "https://royasains.github.io/finalproj_riyavarun/",
  },

    {
    title: "Transportation Noise and its Impact on Health Outcomes in the Northeas",
    blurb:
      "By integrating National Transportation Noise Map data with CDC PLACES health data and US Census socioeconomic indicators, we aim to uncover statistical links between our acoustic environment and our well-being.",  
      href: "https://jasonfan28.github.io/MUSA550-Final-Noise_on_health/",
  },
    {
    title: "Passyunk Square Neighborhood Accessibility Character Map",
    blurb:
      "This site documents the full analytical workflow used to build a multi-dimensional accessibility index for Philadelphia neighborhoods, with a focus on Passyunk Square as a case study.",  
      href: "https://astauf03.github.io/musa5500-python-final/",
  },
    {
    title: "Mapping the Amazon River",
    blurb:
      "In this project, the depth of 12 lakes along the Amazon River was estimated using flooding frequency, with areas that flood more being expected to be deeper. Depth data is valuable for ecological and hydrological research, such as determining biodiversity distribution and modeling water stratification.",  
      href: "https://weijingg.github.io/mapping_amazon/",
  },

  {
    title: "Exploring the relationship between heat stress around bus stops and urban environment: A case study of Philadelphia",
    blurb:
      "Utilizing Universal Thermal Climate Index (UTCI) data throughout Philadelphia to analyze heat stress variations in the immediate vicinity of bus stops.",
    href: "https://zoeyguo709.github.io/Final/",
  },
  {
    title: "Spatial Estimation of Seasonal Variability in Chronic Obtrusive Pulmonary Disease Prevalence Based on Geospatial Machine Learning Procedures",
    blurb:
      "An Approach Using Earth-Engined-Based Remote Sensing Data, Health Risks Behavior, and Socio-Demographic Variables Across Census Tracts in Pennsylvania.",
    href: "https://emilyzhou112.github.io/MUSA550-PA-CRD-Prediction/",
  },
];

export default function FinalProject() {
  return (
    <div className="container project-page">
      {/* Hero */}
      <h1>Final Project</h1>

      <header className="project-hero">
        <div className="badge">Final Project · 45% of final grade</div>
        <p className="lede">
          Replicate the full data-science pipeline on a dataset (or datasets) of your choosing.
          Your final deliverable is a <strong>web-based data visualization</strong> plus a clear write-up of
          <em> collection</em>, <em> analysis</em>, and <em> visualization</em> steps.
        </p>
      </header>

      {/* Due dates */}
      <section className="section">
        <h2>Due Dates</h2>
        <div className="dates-grid">
          <div className="date-card">
            <div className="date-label">Proposal</div>
            <div className="date-value">Thusday, Nov 5 (or earlier)</div>
            <p className="muted">Proposals must be approved in writing before you proceed.</p>
          </div>
          <div className="date-card">
            <div className="date-label">Final Project Report</div>
            <div className="date-value">Monday, Dec 8 @ 11:59 PM</div>
            <p className="muted">A report (~3 pages) summarizing your work, sturctured as introduction, 
              methodology, results, and conclusion.
            </p>
          </div>
        </div>
      </section>

      {/* Deliverables */}
      <section className="section">
        <h2>Deliverables</h2>
        <ol className="list-tight">
          <li>
            <strong>A website</strong> hosted on GitHub Pages.
            Use text, images, and interactive visualizations to explain your process and results. <strong>Vibe coding</strong> is recommended to develop the website and data/map visualizations. 
          </li>
          <li>
            <strong>All project materials</strong> (code, notebooks, spreadsheets, datasets) in your own GitHub repo submited to Canvas.
            Include a <code>README</code> with the URL of your website.
          </li>
          <li>
            <strong>Final project presentation</strong>, all groups/people will present their work on <strong>Dec 4th</strong>, 2026. 
            Prepare a ~10 minutes presentation summarizing your project. Eeach group/person will have about 1~2 minutes for Q&A 
            after the presentation.
          </li>

        </ol>
        <div className="callout">
          <strong>Important:</strong> Put your website URL in the submission on Canvas.
        </div>
      </section>

      {/* Group projects */}
      <section className="section">
        <h2>Group Projects</h2>
        <p>
          Groups up to <strong>3</strong> are permitted. You may combine with work from another course,
          but the portion submitted here must be a clearly defined addition. Scope expectations scale with team size.
        </p>
      </section>

      {/* Requirements */}
      <section className="section">
        <h2>Guidelines & Requirements</h2>
        <div className="req-grid">
          <div className="req-card">
            <div className="req-title">Minimum requirements by group size</div>
            <ul className="req-counts">
              <li><span className="count">2</span> requirements for <strong>1 person</strong></li>
              <li><span className="count">3</span> requirements for <strong>2 people</strong></li>
              <li><span className="count">4</span> requirements for <strong>3 people</strong></li>
            </ul>
            <p className="muted">Shoot for a project roughly 3–4× the scope of a regular assignment.</p>
          </div>
          <div className="req-card">
            <div className="req-title">Possible requirements</div>
            <ul className="bullets">
              {requirements.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
        </div>
      </section>

      {/* Grading */}
      <section className="section">
        <h2>Grading (45%)</h2>
        <div className="table-wrap">
          <table className="rubric-table">
            <thead>
              <tr>
                <th>Criterion</th>
                <th>What we’re looking for</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Concept</strong></td>
                <td>Sufficient complexity and creativity; interesting, useful, or novel outcome.</td>
              </tr>
              <tr>
                <td><strong>Technical implementation</strong></td>
                <td>Sound pipeline; correct methods; consistent with proposal; works as described.</td>
              </tr>
              <tr>
                <td><strong>Visualization</strong></td>
                <td>Clear storytelling; effective layouts, labels, and color choices; interactivity where appropriate.</td>
              </tr>
              <tr>
                <td><strong>Write-up</strong></td>
                <td>Multi-page Quarto site that clearly documents collection, analysis, and visualization steps and results.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Past examples */}
      <section className="section">
        <h2>Examples from Past Semesters</h2>
        <p className="muted">
          Prior years used a different template; visual style may differ from this semester’s Quarto site requirement.
        </p>
        <div className="examples-grid">
          {examples.map((ex) => (
            <a
              key={ex.title}
              className="example-card"
              href={ex.href}
              target="_blank"
              rel="noreferrer"
            >
              <h3>{ex.title}</h3>
              <p>{ex.blurb}</p>
              <span className="more">View project →</span>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}