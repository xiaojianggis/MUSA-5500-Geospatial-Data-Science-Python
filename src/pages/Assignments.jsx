import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./Assignments.css";


const assignments = [
{
    id: "a1",
    title: "HW #1 — Python Basics & Setup",
    assigned: "Thu, Sep 4",
    due: "Sun, Sep 13 @ 11:59 PM",
    detailsMd: `
**Assigned on:** Thu, September 4  
**Due:** Sun, September 13 at 11:59 PM  

---
### Part 1: Installing Python locally and launching Jupyter
- Follow the initial installation guide on the course website to set up Python locally and launch JupyterLab.
- See the recommended readings for \`Python\`, mamba/conda, and \`Jupyter\`.
- Reading
    - Gettting start with Conda ([link](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html))
    - Starting JupyterLab ([Link](https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html))
    - Recommended tutorial for students with little Python background: Practical Python Programming ([link](https://dabeaz-course.github.io/practical-python/Notes/Contents.html))
    - Working with Notebooks in JupyterLab ([Link](https://jupyterlab.readthedocs.io/en/stable/user/notebook.html))
    - Working with files in JupyterLab ([Link](https://jupyterlab.readthedocs.io/en/stable/user/files.html))

### Working Locally
- After activating the course environment, run \`jupyter lab\`.
- Open the notebook \`assignment-1.ipynb\`. You can download it from here, [link](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment-1.ipynb)
- Jupyter runs from the current working directory; get it with \`pwd\`.
- If you cloned the repo, start Jupyter in that folder.


### Part 2: Exploring the Donut Effect (Philadelphia ZIPs)
- Explore the Donut Effect for home values.
- Submit a Jupyter notebook (\`.ipynb\`). A starter notebook is in the repo.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook to Canvas directly, not as a GitHub link.
    `
},
{
    id: "a2",
    title: "HW #2 — Exploratory Data Visualization",
    assigned: "Thu, Sep 11",
    due: "Sun, Sep 21 @ 11:59 PM",
    detailsMd: `
**Assigned on:** Thu, September 11 
**Due:** Sun, September 21 at 11:59 PM  

---
### Part 1: Part 1: Select a dataset

In this part, you’ll use matplotlib, seaborn, and altair to explore a dataset of your choosing and generate some charts in a Jupyter notebook.


For this assignment, you can choose your own dataset to explore. I recommend selecting a dataset from OpenDataPhilly. You are welcome to to use a dataset from elsewhere, but please email your instructor and let them know what you want to analyze.

Datasets with timestamped entries will be particularly good for analysis, but there are many interesting datasets to consider. They include:

- [311 Requests](https://www.opendataphilly.org/dataset/311-service-and-information-requests)
- [Voter turnout](https://opendataphilly.org/datasets/voter-turnout/)
- [Parking violations](https://opendataphilly.org/datasets/parking-violations/)
- [Shooting victims](https://opendataphilly.org/datasets/shooting-victims/)
- and many more…


### Part 2: Explore and visualize the data

From within a Jupyter notebook, you should explore the datasets and generate charts visualizing different aspects of the data.

Requirements:

- **1 Matplotlib chart** (of any type)
You should consider what aspect of the dataset might be best plotted using matplotlib.
Include your reasoning for using matplotlib to visualize this specific aspect of the data.
You will be graded on the aesthetics of the plot, namely, color choices and clarity.

- **1 seaborn chart** (of any type)
Please include the motivation behind your choice for the type of seaborn plot used and why.

- **3 altair plots**
Both of the following techniques should be used:
  - A transformation (mean, count, binning, etc)
  - Brush selection
Include a short discussion (a few sentences) of the main conclusion of each chart (in a markdown cell below each chart). It does not need to be interesting or insightful, but it is good practice to always note the main conclusions so the notebook make sense after time passes.

- **Extra credit** 2-chart altair dashboard,
This should be in addition to the 3 charts above
Filtering on one chart should cross-filter the other chart (via transform_filter())
Note: You may include geospatial charts to satisfy the above requirements, but you are not required to.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook and you data to Canvas directly using relative path.
    `
} ,
{
  id: "a3",
  title: "HW #3 — Explore spatial patterns",
  assigned: "Thu, Sep 25",
  due: "Tue, Oct 12 @ 11:59 PM",
  detailsMd: `
**Assigned on:** Thu, September 25 
**Due:** Tue, Oct 12 at 11:59 PM  
### Description
---
This assignment will include two parts:

In Part 1, we’ll explore spatial trends evictions in Philadelphia using data from the [Eviction Lab](https://evictionlab.org/) and building code violations using data from [OpenDataPhilly](https://www.opendataphilly.org/).

We’ll be exploring the idea that evictions can occur as retaliation against renters for reporting code violations. Spatial correlations between evictions and code violations from the City’s Licenses and Inspections department can offer some insight into this question.

In Part 2, we’ll dive into the NDVI in Philadelphia more. Using Landsat data, we’ll calculate the NDVI within the city limits and compare it to the NDVI in the immediate suburbs. We’ll also calculate the NDVI at the locations of trees in Philadelphia, using a dataset of street trees from OpenDataPhilly.

### Background readings
- [**HuffPost article**](https://www.huffpost.com/entry/cities-are-starting-to-pay-attention-to-the-eviction-crisis-thats-devastated-poor-tenants_n_5b1a7b21e4b0bbb7a0dbd59e)
- [**PlanPhilly article**](https://whyy.org/segments/philly-landlords-evict-more-people-than-owners-in-other-large-cities/)
- [**The Eviction Lab**](https://evictionlab.org/)
- [**Data Dictionary for Eviction Lab**]() data available for download in this repository


### Assignment details

All the data can be download from [**HERE**](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment3-data.zip). Please download it on your working directory. 
A [skeleton Jupyter notebook](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment-3.ipynb) is available in this repository that will walk you through the steps of the assignment. 
Please unzip the data.zip and put it in the same folder as the notebook. The completed notebook should be submitted as your assignment.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook and you data to Canvas directly using relative path.
  `
} ,
{
  id: "a4",
  title: "HW #4 — Network Analysis & Web Scraping",
  assigned: "Thu, Oct 16",
  due: "Tue, Nov 7 @ 11:59 PM",
  detailsMd: `
**Assigned on:** Thu, Oct 16 
**Due:** Tue, Nov 7 at 11:59 PM  
### Description
---
This assignment will include two parts:

**Part 1: Visualizing crash data in Philadelphia**

In this section, you will use osmnx to analyze the crash incidence in Center City.

**Part 2: Scraping Craigslist**
In this section, you will use Selenium and BeautifulSoup to scrape data for hundreds of apartments from Philadelphia’s Craigslist portal.


### Assignment details
A [skeleton Jupyter notebook](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment-4.ipynb) 
is available in this repository that will walk you through the steps of the assignment. The completed notebook should be submitted as your assignment.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook and you data to Canvas directly using relative path.
  `
} ,
{
  id: "a5",
  title: "HW #5 — Restaurant reviews and census data",
  assigned: "Thu, Nov 6",
  due: "Tue, Nov 13 @ 11:59 PM",
  detailsMd: `
**Assigned on:** Thu, Nov 6 
**Due:** Thu, Nov 13 at 11:59 PM  
### Description
---
In this assignment, we’ll explore restaurant review data available through the [Yelp Dataset Challenge](https://business.yelp.com/data/resources/open-dataset/).
 The dataset includes Yelp data for user reviews and business information for many metropolitan areas.
  I’ve already downloaded this dataset (8 GB total!) and extracted out the data files for reviews 
  and restaurants in Philadelphia. I’ve placed these data files into the data directory in this repository.

**Analyzing correlations between restaurant reviews and census data**

We’ll explore the relationship between restaurant reviews and the income levels of the restaurant’s surrounding area.


### Assignment details
A [skeleton Jupyter notebook](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment-5.ipynb) 
is available in this repository that will walk you through the steps of the assignment. The completed notebook should be submitted as your assignment.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook and you data to Canvas directly using relative path.
  `
}, 
{id: "a6",
title: "HW #6 — Predicting Housing Prices in Phily",
assigned: "Thu, Nov 13",
due: "Monday, Nov 24 @ 11:59 PM",
detailsMd: `
**Assigned on:** Thu, Nov 13 
**Due:** Monday, Nov 24 at 11:59 PM
### Description
---
Lectures 12B and 13A, B will cover predictive modeling of housing prices in Philadelphia. In this assignment,
we'll extend that analysis in this section by:

- Optimizing our hyperparameters during the modeling process using cross-validation and a grid search
- Testing the fairness of our model by calculating the intersection of the model error rate and poverty rate across neighborhoods

**Predictive Modeling of Housing Prices in Philadelphia**


### Assignment details
A [skeleton Jupyter notebook](https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python/blob/main/public/assignments/assignment-6.ipynb) 
is available in this repository that will walk you through the steps of the assignment. The completed notebook should be submitted as your assignment.


### Submission Notes
- Submit via **Canvas**. Please submit your notebook and you data to Canvas directly using relative path.
`
}
];



//   // Add more assignments with `detailsMd` (markdown)…
//   {
//     id: "a2",
//     title: "HW #2 — Pandas & Visualization",
//     assigned: "Wed, Oct 2",
//     due: "Mon, Oct 14 @ 11:59 PM",
//     detailsMd: `
// **Materials:** [assignment-2 (starter)](#)  
// **Submission:** GitHub Classroom

// ### Overview
// Work with tabular datasets in **Pandas** and create exploratory plots using **Matplotlib**.  
// Please include inline interpretations below each figure.

// - Load, clean, and describe the dataset  
// - Create at least **3** diagnostic plots  
// - Discuss findings (3–5 bullet points)
//     `
//   }



export default function Assignments() {
  const [openId, setOpenId] = useState(null);
  const toggle = (id) => setOpenId((cur) => (cur === id ? null : id));

  return (
    <div className="container assignments-page">
          <h2 id="guidelines">Guidelines</h2>
          <p>
            There are several homework assignments during the term and one final
            project at the end. Your lowest assignment grade is dropped.Assignments are submitted as Jupyter notebooks. To streamline grading,
            please follow these practices:
          </p>

          <ol>
            <li>
              <strong>Polished notebooks:</strong>
              <ul>
                <li>Include your name (and any collaborators) at the top.</li>
                <li>Remove unused or exploratory fragments.</li>
                <li>Use Markdown cells and/or code comments to explain steps.</li>
                <li>Use section headings to organize your analysis.</li>
              </ul>
            </li>
            <li>
              <strong>Reproducible and executable:</strong>
              <ul>
                <li>Ensure the notebook runs top‑to‑bottom without errors.</li>
                <li>
                  If you use data, either include it in your repo or clearly
                  document the source so it can be downloaded for grading.
                </li>
                <li>
                  Use <em>relative</em> file paths so the repo structure works
                  when cloned. See the course note on file paths for more detail.
                </li>
              </ul>
            </li>

            <li>
              <strong>Submit your notebook to Canvas</strong>
                <ul>
                  <li>
                    Please submit your assigment together with your data to canvas. 
                  </li>
                  <li>You can upload the zipped file or just sumbit all of them together. 
                    
                  </li>
                </ul>
              </li>
          </ol>

      <h2>Assignments</h2>

      <div className="table-wrap">
        <table className="assignments-table">
          <thead>
            <tr>
              <th style={{width:"40%"}}>Assignment</th>
              <th style={{width:"20%"}}>Assigned</th>
              <th style={{width:"25%"}}>Due</th>
              <th style={{width:"15%"}}>Details</th>
            </tr>
          </thead>
          <tbody>
            {assignments.map(a => {
              const expanded = openId === a.id;
              const panelId = `${a.id}-panel`;
              return (
                <React.Fragment key={a.id}>
                  <tr className={`a-summary ${expanded ? "is-open" : ""}`}>
                    <td>
                      <button
                        className="a-toggle"
                        aria-expanded={expanded}
                        aria-controls={panelId}
                        onClick={() => toggle(a.id)}
                      >
                        <span className="a-title">{a.title}</span>
                        <span className="a-chevron" aria-hidden>▸</span>
                      </button>
                    </td>
                    <td>{a.assigned}</td>
                    <td>{a.due}</td>
                    <td className="a-actions">
                      <button
                        className="a-ghost"
                        aria-expanded={expanded}
                        aria-controls={panelId}
                        onClick={() => toggle(a.id)}
                      >
                        {expanded ? "Hide" : "View"}
                      </button>
                    </td>
                  </tr>

                  {expanded && (
                    <tr className="a-details-row">
                      <td id={panelId} colSpan={4}>
                        <div className="a-details markdown-body">
                          <ReactMarkdown>{a.detailsMd}</ReactMarkdown>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
