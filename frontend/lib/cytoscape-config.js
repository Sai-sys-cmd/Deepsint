export const cytoscapeConfig = {
  style: [
    // Node base styles
    {
      selector: "node",
      style: {
        "background-color": "oklch(0.488 0.243 264.376)", // primary color
        "label": "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "font-size": "12px",
        "font-family": "Inter, sans-serif",
        "width": "data(size)",
        "height": "data(size)",
        "border-width": 2,
        "border-color": "oklch(0.985 0.001 106.423)", // primary-foreground
        "text-wrap": "wrap",
        "text-max-width": "100px",
      },
    },
    // Platform-specific colors
    {
      selector: "node[platform='github']",
      style: { "background-color": "oklch(0.268 0.007 34.298)" }, // secondary
    },
    {
      selector: "node[platform='reddit']", 
      style: { "background-color": "oklch(0.704 0.191 22.216)" }, // destructive
    },
    {
      selector: "node[platform='twitter']",
      style: { "background-color": "oklch(0.488 0.243 264.376)" }, // primary
    },
    {
      selector: "node[platform='breach']",
      style: { "background-color": "oklch(0.704 0.191 22.216)", "border-color": "oklch(0.577 0.245 27.325)" }, // destructive colors
    },
    // Risk-based styling
    {
      selector: "node[risk='high']",
      style: { "border-width": 4, "border-color": "oklch(0.704 0.191 22.216)" }, // destructive
    },
    {
      selector: "node[risk='medium']",
      style: { "border-width": 3, "border-color": "oklch(0.769 0.188 70.08)" }, // chart-5 (amber-like)
    },
    // Edge styles
    {
      selector: "edge",
      style: {
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "line-color": "oklch(0.553 0.013 58.071)", // muted-foreground
        "target-arrow-color": "oklch(0.553 0.013 58.071)", // muted-foreground
        "width": "data(strength)",
        "label": "data(relation)",
        "font-size": "10px",
        "text-rotation": "autorotate",
      },
    },
  ],
  layout: {
    name: "cose",
    idealEdgeLength: 100,
    nodeOverlap: 20,
    refresh: 20,
    fit: true,
    padding: 30,
    animate: true,
    animationDuration: 1000,
  },
};

export const personaColors = {
  developer: "oklch(0.646 0.222 41.116)", // chart-1 (green)
  social: "oklch(0.488 0.243 264.376)",    // primary (blue)  
  suspicious: "oklch(0.769 0.188 70.08)", // chart-5 (amber)
  compromised: "oklch(0.704 0.191 22.216)", // destructive (red)
  professional: "oklch(0.627 0.265 303.9)", // chart-4 (purple)
};