import React from "react";
// import "../styles/design.css"
import "./Syllabus.css"

export default function Syllabus() {
  const schedule = [
    { w: 1, date: "8/27/26", topic: "Course introduction and programming environment setup", lab: "Configure the environment of Anaconda, Jupyter Notebook, Visual Studio Code, Python basics (Python modules, read/write txt and csv files, file operations, exception handling, functions)" },
    { w: 2, date: "9/3/26", topic: "Data Visualization Fundamentals", lab: "Read file and create visualizations using Pandas, Matplotlib" },
    { w: 3, date: "9/10/26", topic: "More on Data Visualization and Intro to Vector Data", lab: "Read file and create visualizations using Pandas, Matplotlib" },
    { w: 4, date: "9/17/26", topic: "Geospatial data mapping", lab: "Use GeoPandas and Leaflet to do analysis and create maps" },
    { w: 5, date: "9/24/26", topic: "Raster data operations in Python", lab: "Using Rasterio and NumPy, XArray to manipulate raster data" },
    { w: 6, date: "10/1/26", topic: "Fall break — No class" },
    { w: 7, date: "10/8/26", topic: "Advanced geospatial analysis", lab: "Zonal statistics overlay polygon on rasters, road network analysis (NetworkX, OSMnx)" },
    { w: 8, date: "10/15/26", topic: "Web Scraping", lab: "Web scrape through API, parse the HTML of web pages, store the data in database" },
    { w: 9, date: "10/22/26", topic: "Web Scraping (II)", lab: "Web scrape and analyze the real data, GSV…" },
    { w: 10, date: "10/29/26", topic: "Analyzing and Visualizing Large Datasets", lab: "Visualize large raster data and the vector data, LiDAR data processing" },
    { w: 11, date: "11/5/26", topic: "Web hosting", lab: "Python + web application, Vibe coding for web application" },
    { w: 12, date: "11/12/26", topic: "Machine learning (I)", lab: "Predictive Modeling with Scikit-Learn" },
    { w: 13, date: "11/19/26", topic: "Machine learning (II)", lab: "Predictive Modeling with Scikit-Learn" },
    { w: 14, date: "11/26/26", topic: "Thanksgiving break — No class" },
    { w: 15, date: "12/3/26", topic: "Final Project Presentations (last day of class)" },
  ];

  return (
    <div className="syllabus">
      <header className="page-hero syllabus-hero">
        <div className="badge">Fall 2026 · MUSA 5500 / CPLN 6720</div>
        <h1>Geospatial Data Science in Python</h1>

        <div className="hero-grid">
          <div className="hero-card">
            <h3>Logistics</h3>
            <ul>
              <li><strong>Meets:</strong> Thursday, 1:45–4:44 PM</li>
              <li><strong>Location:</strong> Neural and Behavioral Sciences Building, NBS 111</li>
            </ul>
          </div>
          <div className="hero-card">
            <h3>Instructor</h3>
            <ul>
              <li><strong>Name:</strong> Xiaojiang Li</li>
              <li><strong>Office:</strong> Meyerson Hall 407</li>
              <li><strong>Email:</strong> <a href="mailto:jianglix@design.upenn.edu">jianglix@design.upenn.edu</a></li>
              <li><strong>Office Hours:</strong> Thu 11:00 AM – 12:00 PM</li>
            </ul>
          </div>
        </div>
      </header>

      <section className="section">
        <h2>Overview</h2>
        <p>
        This course will provide students with the knowledge and tools to turn data into meaningful insights, with a focus on real-world case studies in the urban planning and public policy realm. Focusing on the latest Python software tools, the course will outline the “pipeline” approach to data science. It will teach students the tools to gather, manipulate, visualize, and analyze datasets, providing the skills to effectively explore geospatial datasets and transform results into understandable and compelling narratives. The course is organized into five main sections:
        </p>

        <ol className="list-tight">
          <li><strong>Exploratory Data Science:</strong> Students will be introduced the basics of Python, data structure, read and write different types of files, string operations, loops, and functions/classes. Students will be introduced to the main tools needed to get started analyzing and visualizing data using Python.</li>
          <li><strong>Introduction to Geospatial Data Science:</strong> Building on the previous set of tools, this module will teach students how to work with geospatial datasets using a range of modern Python toolkits.</li>
          <li><strong>Data Ingestion & Big Data:</strong> Students will learn how to collect new data through web scraping and APIs, as well as how to work effectively with the large datasets often encountered in real-world applications.</li>
          <li><strong>From Exploration to Storytelling:</strong> With a solid foundation, students will learn the latest tools to present their analysis results using web-based formats to transform their insights into interactive stories.</li>
          <li><strong>Geospatial Data Science in the Wild:</strong> Armed with the necessary data science tools, the final module introduces a range of advanced analytic and machine learning techniques using a number of innovative examples from modern researchers.</li>
        </ol>
      </section>

      <section className="section">
        <h2>Lecture & Lab</h2>
        <p>
        The lecture part is focus on explaining the concepts, theories, and best practices for writing Python script. The lecture is intended, as much as possible, to be an interactive environment.  Please feel free at any time during the lecture to ask a question or make a comment. Conversely, you are expected to respond to discussion questions asked in class.
        </p>

        <p>The remainder of each class following the lecture will be devoted to the lab.  During the lab, students work on lab assignments that provide practical experience in applying the concepts learned in the lecture. You are highly recommended to have your own machine for this class. </p>
      </section>

      <section className="section">
        <h2>Assignments & Final Project</h2>
        <p>
          There are six homework assignments and one required final project at the end of the semester. While you are required to submit all six assignments, the assignment with the lowest grade will not count towards your final grade.
          
        </p>
        <p>        
          For the final project, students will replicate the pipeline approach on a dataset (or datasets) of their choosing. Students will be required to use several of the analysis techniques taught in the class and produce a web-based data visualization that effectively communicates the empirical results to a non-technical audience. The final product should also include a description of the methods used in each step of the data science process (collection, analysis, and visualization).
        </p>

        <p>See the Final Project page for details.</p>
      </section>

      <section className="section two-col">
        <div>
          <h2>Grading</h2>
          <ul>
            <li>Homework: 50%</li>
            <li>Final Project: 45%</li>
            <li>Participation: 5% (presence in the class)</li>
          </ul>
          <p className="muted">
            No late penalty. You’ll miss faster feedback, but your score isn’t reduced.
          </p>
        </div>
        <div>
          <h3 className="mt-0">Letter Grades</h3>
          <table className="grade-table">
            <tbody>
              <tr><td>100–95.00%</td><td>A</td></tr>
              <tr><td>94.99–90.00%</td><td>A-</td></tr>
              <tr><td>89.99–87.00%</td><td>B+</td></tr>
              <tr><td>86.99–84.00%</td><td>B</td></tr>
              <tr><td>83.99–80.00%</td><td>B-</td></tr>
              <tr><td>79.99–77.00%</td><td>C+</td></tr>
              <tr><td>76.99–74.00%</td><td>C</td></tr>
              <tr><td>73.99–70.00%</td><td>C-</td></tr>
              <tr><td>69.99–67.00%</td><td>D+</td></tr>
              <tr><td>66.99–60.00%</td><td>D</td></tr>
              <tr><td>59.99–0.00%</td><td>F</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="section">
        <h2>Software</h2>
        <p>
        This course relies on use of Python and various related packages and for geospatial topics. All software is open-source and freely available. The course will require a working installation of Python on your local computer.         </p>
      </section>

      <section className="section">
        <h2>Policies</h2>
        <p>
        MUSA 5500 is a fast-paced course that covers a lot of topics in a short amount of time. I know that it can be overwhelming and frustrating, particularly as you are trying to learn Python syntax and the topics in the course at the same time. But I firmly believe that all students can succeed in this class.You’ll get the most out of the course if you stay up to date on the lectures and assignments. If you fall behind, I know there can be a desire to copy code from the Internet or others to help you complete assignments. Ultimately, this will be detrimental to your progress as an analytics wizard. My goal for this course is for everyone to learn and engage with the material to the best of their ability. If you find yourself falling behind or struggling with Python issues, please ask for help by:
        </p>
        <ol className="list-tight">
          <li>Come to office hours to discuss issues or larger conceptual questions.</li>
          <li>Use free resources to fine-tune Python skills.</li>
          <li>If you’re still struggling, reach out so we can make a plan.</li>
        </ol>

        <p><strong>Note:</strong> And if you are still struggling, reach out and let me know and we’ll figure out a strategy to make things work! NOTE: AI for coding (vibe coding) make lot of things very easy now. However, this class is the basic level of Python, I still recommend you <strong>MINIMIZE</strong>  the usage of AI for your work. AI can also help you to learn Python, like when you are confused on some script, you can ask AI to help you understand it. Try to not ask AI to help you do all the work now in this class. </p>
      </section>

      <section className="section">
        <h2>Communication Policies</h2>
        <ul className="list-tight">
          <li>Please add the following text into the subject line of emails to us: [MUSA550]. This will help us make sure we don’t miss your email!</li>
          <li>If you have larger-scale or conceptual questions on assignments or lecture material, please set up a time to discuss during office hours.</li>

        </ul>
      </section>

      <section className="section">
        <h2>Group Work</h2>
        <p>
        Students are allowed (and encouraged!) to collaborate when working through lecture materials or assignments. If you work closely with other students, please list the members of your group at the top of your assignment.
        </p>
      </section>

      <section className="section">
        <h2>Special Accommodations</h2>
        <p>
        There are a number of ongoing situations in the world that may take precedence over the course work. If you are experiencing any difficulties outside the course, please contact me and accommodations can be made. Similarly, if you are having any difficulties with the course schedule, attending lectures, or similar, please let us know.
        </p>
      </section>

      <section className="section">
        <h2>Academic Integrity</h2>
        <p>
        Since the University is an academic community, its fundamental purpose is the pursuit of knowledge. Essential to the success of this educational mission is a commitment to the principles of academic integrity. Every member of the University community is responsible for upholding the highest standards of honesty at all times. Students, as members of the community, are also responsible for adhering to the principles and spirit of the following Code of Academic Integrity. For more details about the academic dishonesty definitions,  https://catalog.upenn.edu/pennbook/code-of-academic-integrity/
        </p>
      </section>

      <section className="section">
        <h2>Textbook</h2>
        <p>No textbook required. Papers and online materials will be provided on the course website.</p>
      </section>

      <section className="section">
        <h2>Disabilities</h2>
        <p>
        The University of Pennsylvania is committed to the accessibility of its programs and services. Students with a disability or medical condition can request reasonable accommodations through the Weingarten Center website. Disability Services determines accommodations on an individualized basis through an interactive process, including a meeting with the student and a review of their disability documentation. Students who have approved accommodations are encouraged to notify their faculty members and share their accommodation letters at the start of each semester. Students can contact Disability Services by calling 215-573-9235.
        </p>
      </section>

      <section className="section">
        <h2>Classroom Environment</h2>
        <p>All persons participating in the course should be respectful of other students and the instructor in order to facilitate a civil learning environment.  All persons participating in the course have a right to expect respectful treatment in the classroom.</p>
      </section>

      <section className="section">
        <h2>Course Schedule</h2>
        <div className="table-wrap">
          <table className="schedule-table">
            <thead>
              <tr>
                <th>Week</th>
                <th>Day</th>
                <th>Topic</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map(r => (
                <tr key={`${r.w}-${r.date}`}>
                  <td>{r.w}</td>
                  <td>{r.date}</td>
                  <td>
                    {r.w === 1 || r.topic.toLowerCase().includes("break") || r.w === 15
                      ? r.topic
                      : <><strong>Lecture:</strong> {r.topic}</>}
                    {r.lab && <><br /><strong>Lab:</strong> {r.lab}</>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
