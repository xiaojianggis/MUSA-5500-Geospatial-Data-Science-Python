import React from "react";
import "./Schedule.css";

// If you deploy under a base path (e.g., GitHub Pages), BASE_URL helps build correct links
const base = import.meta.env.BASE_URL || "/";

const schedule = [
  { w: 1, date: "8/27/26", topic: "Course introduction and programming environment setup",
    // multiple labs → different HTMLs
    lab: [
      { label: "1.1 Environment setup and Python basics",  href: `${base}labs/week-1-intro-python/week-1A-python-basics.html` },
      { label: "1.2 More about Python", href: `${base}labs/week-1-intro-python/week-1B-more-about-python.html` },
    ],
  },
  { w: 2, date: "9/3/26", topic: "Data Visualization Fundamentals",
    // if you just give strings, we’ll auto-map to lab{ww}-{index}.html
    lab: [ 
      { label: "2.1 Exploratory data science", href: `${base}labs/week-2-data-viz-fundamentals/week-2A-exploratory-data-science-Python.html`  },
      { label: "2.2 data visualization fundamentals-A", href: `${base}labs/week-2-data-viz-fundamentals/week-2B1-data-visualization-fundamentals-A.html` },
      { label: "2.3 data visualization fundamentals-B", href: `${base}labs/week-2-data-viz-fundamentals/week-2B2-data-visualization-fundamentals-B.html` }
    ],
  },
  { w: 3, date: "9/10/26", topic: "More on Data Visualization and Intro to Vector Data & GeoPandas",
    // single string → auto-map to lab{ww}.html
    lab: [
      {label: "3.1 More about data visualization" /* href: `${base}labs/week-3-more-data-viz-geodata/week-3-more-data-viz.html` */},
      {label: "3.2 Intro to GeoPandas and vector data" /* href: `${base}labs/week-3-more-data-viz-geodata/week3-geospatial-data-concepts.html` */}
    ]
  },
  { w: 4, date: "9/17/26", 
    topic: "Geospatial data mapping", 
    lab: [
      {label: "4.1 More about geospatial data mapping" /* href: `${base}labs/week-4-spatial-data-mapping/week-4A-spatial-data-viz.html` */},
      {label: "4.2 Interactive spatial data visualization" /* href: `${base}labs/week-4-spatial-data-mapping/week-4B-interactive-spatial-data-viz.html` */}
    ]
  },
  { w: 5, date: "9/24/26", topic: "Raster data operations in Python", 
    lab: [
      {label: "5.1 Raster data operations" /* href: `${base}labs/week-5-raster-analysis/week-5A-raster-data.html` */},
      {label: "5.2 Raster data analysis" /* href: `${base}labs/week-5-raster-analysis/week-5B-raster-analysis.html` */}
    ]
  },
  { w: 6, date: "10/1/26", topic: "Fall break — No class", 
    lab: "—" 
  },
  { w: 7, date: "10/8/26", topic: "Advanced geospatial analysis", 
    lab: [
      {label: "6.1 Advanced geospatial analysis" /* href: `${base}labs/week-6-advanced-geospatial-analysis/week-6A-advanced-raster-analysis.html` */},
      {label: "6.2 Zonal statistics" /* href: `${base}labs/week-6-advanced-geospatial-analysis/week-6B-spatial_fiona_shapely.html` */}
    ]
  },
  // { w: 8, date: "10/15/26", topic: "Network analysis", 
  //   lab: [
  //     {label: "8.1 Network analysis with OSMnx" /* href: `${base}labs/week-8-network-analysis/week-8A-street-network.html` */},
  //     {label: "8.2 Basics of Graph and NetworkX" /* href: `${base}labs/week-8-network-analysis/week-8B-street-network.html` */}
  //   ]
  // },
  { w: 8, date: "10/15/26", topic: "Web Scraping", 
    lab: [
      {label: "9.1 Web Scraping (I)" /* href: `${base}labs/week-9-web-scraping/lecture-9A.html` */},
      {label: "9.2 Web Scraping (II)" /* href: `${base}labs/week-9-web-scraping/lecture-9B.html` */}
    ]
  },
  { w: 10, date: "10/22/26", topic: "Web Scraping (II)", 
    lab: [
      {label: "10.1 Web APIs (I)" /* href: `${base}labs/week-10-web-api/lecture-10A.html` */},
      {label: "10.2 Web APIs (II)" /* href: `${base}labs/week-10-web-api/lecture-10B.html` */}
    ]
  },
    { w: 11, date: "10/29/26", topic: "Analyzing and Visualizing Large Datasets", 
    lab: [
      {label: "10.1 Visualizing large datasets" /* href: `${base}labs/week-10-web-api/lecture-10A.html` */},
      {label: "10.2 LiDAR data processing" /* href: `${base}labs/week-10-web-api/lecture-10B.html` */}
    ]
  },
  { w: 11, date: "11/5/26", topic: "Web hosting: GitHub, Vibe coding, create web pages", 
    lab: "Publish notebooks & sites" 
  },
  { w: 12, date: "11/12/26", topic: "Machine Learning (I)", 
    lab: [
      {label: "12.1 Clustering Analysis (I)" /* href: `${base}labs/week-12-cluster-analysis/lecture-12A.html` */},
      {label: "12.2 Clustering Analysis (II)" /* href: `${base}labs/week-12-cluster-analysis/lecture-12B.html` */},
      {label: "12.3 Predictive modeling (I)" /* href: `${base}labs/week-13-machine-learning-scikit/lecture-13A.html` */}
    ]
  },
  { w: 13, date: "11/19/26", topic: "Machine Learning (II)", 
    lab: [
      {label: "13.1 Predictive modeling (II)" /* href: `${base}labs/week-13-machine-learning-scikit/lecture-13B.html` */},
      {label: "13.2 Predictive modeling (III)" /* href: `${base}labs/week-14-predictive-modeling/lecture-14A.html` */},
      {label: "Deep learning" /* href: `${base}labs/week-14-predictive-modeling/deep-learning.html` */}
    ]
  },
  { w: 14, date: "11/26/26", topic: "Thanksgiving break — No class", 
    lab: "—" 
  },
  { w: 15, date: "12/3/26", topic: "Final Project Presentations (last day of class)", 
    lab: "—" 
  },
];

function LabCell({ item }) {
  const val = item.lab;

  if (val === "—" || val == null) return <span>—</span>;

  if (Array.isArray(val) && val.every(v => v && typeof v === "object")) {
    return (
      <ul className="lab-list">
        {val.map((lab, i) => (
          <li key={`${item.w}-labobj-${i}`}>
            {lab.href ? <a href={lab.href}>{lab.label}</a> : <span>{lab.label}</span>}
          </li>
        ))}
      </ul>
    );
  }

  // String-based lab entries are also plain text while links are disabled.
  if (Array.isArray(val)) {
    return (
      <ul className="lab-list">
        {val.map((label, i) => (
          <li key={`${item.w}-lab-${i}`}>
            <span>{label}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (typeof val === "string") {
    return <span>{val}</span>;
  }

  
  return <span>—</span>;
}


export default function Schedule() {
  return (
    <div className="container schedule-page">
      <h2>Schedule</h2>
      <p>Below is the tentative weekly schedule for MUSA 5500.</p>

      <div className="table-wrap">
        <table className="schedule-table">
          <thead>
            <tr>
              <th>Week</th>
              <th>Date</th>
              <th>Topic</th>
              <th>Lab</th>
            </tr>
          </thead>

          <tbody>
            {schedule.map((item) => (
              <tr key={item.w}>
                <td>{item.w}</td>
                <td>{item.date}</td>
                {/* Topic is plain text (no link) */}
                <td>{item.topic}</td>
                {/* Lab links are temporarily disabled. */}
                <td><LabCell item={item} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
