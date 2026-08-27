import React from 'react'
// import "./syllabus.css"; // Optional: if you want local styles
import "./Home.css"
import { Link } from 'react-router-dom';

const base = import.meta.env.BASE_URL; // "/MUSA-5500-Geospatial-Data-Science-Python/" in prod

function Card({ title, description, link, linkText }) {
    return (
        <div className="card">
        <h2>{title}</h2>
        <p>{description}</p>
        <Link to={link} className="button">{linkText}</Link>
        </div>
    );
}

export default function Home(){
    return (
        <div className="container">
          <section className="hero">
            <h2 className="hero-title">Welcome to MUSA5500 Geosptial Data Science in Python</h2>
            <div className='hero-content'>
                <div className='hero-text'>
                    <h2>
                        Use Python to gather, visualize, and analyze geospatial data with an urban planning and public policy focus
                    </h2>
                    <div className='hero-subtitle'>
                        Spatial Data Science in Python is a graduate-level course in the MUSA program at the University of Pennsylvania. 
                        Learn to work with spatial data in Python for analysis, visualization, and decision-making.
                    </div>
                    <br />

                    <div className="instructors-card" aria-labelledby="course-meta-heading">
                    <h3 id="course-meta-heading" className="meta-title">Course team & contact</h3>

                    <div className="meta-grid">
                      <div className="meta-block meta-span">
                        <div className="meta-label">Instructor</div>
                        <div className="meta-value">
                          Xiaojiang Li, PhD ·{" "}
                          <a href="mailto:jianglix@design.upenn.edu" className="contact-link">
                            jianglix@design.upenn.edu
                          </a>
                        </div>
                        <div className="meta-value">
                          Office hour: by appointment
                        </div>
                      </div>

                      <div className="meta-block meta-span">
                      <div className="meta-label">TA</div>



                        <br />
                        <div className="meta-value">
                          Zhanchao Yang·{" "}
                          <a href="mailto:zhanchao@design.upenn.edu" className="contact-link">
                            zhanchao@design.upenn.edu
                          </a>
                          <br />
                          {" Office hour:"} Mon, 1:30 to 3:30pm, <a href="https://calendly.com/deng13-upenn/office-hour">Schedule</a>, <a href="https://upenn.zoom.us/j/2100517683">Zoom Link</a>
                        </div>

                      </div>


                      <div className="meta-block meta-span">
                        <div className="meta-label">Classroom</div>
                        <div className="meta-value">
                          Neural and Behavioral Sciences Building, <a href="https://facilities.upenn.edu/maps/locations/neural-behavioral-sciences-building" target="_blank" rel="noopener noreferrer">NBS 111</a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="hero-image">
                <img
                  src={`${base}images/maps.png`}
                  alt="MUSA Geospatial" 
                />
            </div>
            </div>
          </section>
          
          <section className="section">
            <h3 className="section-title">Course Navigation</h3>
            <div className="card-grid">
                <Card 
                    title="Syllabus" 
                    description="Review course structure, grading policy, schedule, and required tools." 
                    link="/syllabus" 
                    linkText="View Syllabus"
                />


              <Card 
                title="Schedule" 
                description="Access weekly lectures, hands-on notebooks, and practical demos." 
                link="/schedule" 
                linkText="View Weekly Schedule"
              />


              <Card
                title="Assignments"
                description="Review assignment guidelines and access homework materials."
                link="/assignments"
                linkText="View Assignments"
              />

              <Card 
                title="Final Project" 
                description="Tackle a real-world geospatial problem using Python and present your results." 
                link="/project" 
                linkText="Final Project"
              />

            </div>
          </section>
        </div>
      );
}
