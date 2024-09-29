import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Alert } from "./Alert";

function App() {
  // State variables for user inputs
  const [selectedMethod, setSelectedMethod] = useState<string>("Random");
  const [numClusters, setNumClusters] = useState<number>(3); // Default to 3 clusters
  const [numPoints, setNumPoints] = useState<number>(100); // Number of points for the dataset
  const [imageSrc, setImageSrc] = useState<string | null>(null); // State to hold the graph image
  const [hasGenDataset, setHasGenDataset] = useState<boolean>(false);
  const [hasInitialized, setHasInitialized] = useState<boolean>(false); // Track initialization state
  const [hasConverged, setHasConverged] = useState<boolean>(false); // Track convergence state
  const [manualCentroids, setManualCentroids] = useState<number[][]>([]);
  const [centroidMessages, setCentroidMessages] = useState<string[]>([]); // State to hold messages

  const handleSelect = (method: string) => {
    setSelectedMethod(method);
    if (method !== "Manual") {
      setManualCentroids([]); // Clear manual centroids when switching methods
      setCentroidMessages([]); // Clear messages when not in manual mode
    }
  };

  const handlePlotClick = (
    e: React.MouseEvent<HTMLImageElement, MouseEvent>
  ): void => {
    if (selectedMethod === "Manual") {
      // Prevent selecting more than the number of clusters
      if (manualCentroids.length >= numClusters) {
        alert("You have selected the maximum number of centroids.");
        return;
      }

      const boundingRect = e.currentTarget.getBoundingClientRect();
      const x = ((e.clientX - boundingRect.left) / boundingRect.width) * 100;
      const y = ((e.clientY - boundingRect.top) / boundingRect.height) * 100;

      const newCentroid = [x, y];
      setManualCentroids((prevCentroids) => [...prevCentroids, newCentroid]);

      // Add a message showing the coordinates
      const pointNumber = manualCentroids.length + 1;
      const newMessage = `Point ${pointNumber} initialized at (${x.toFixed(
        2
      )}, ${y.toFixed(2)})`;
      setCentroidMessages((prevMessages) => [...prevMessages, newMessage]);
    }
  };

  useEffect(() => {
    if (manualCentroids.length === numClusters) {
      handleManualInitialize();
    }
  }, [manualCentroids]);

  const handleManualInitialize = (): void => {
    axios
      .post("http://localhost:5000/initialize-clustering", {
        numClusters: numClusters,
        initMethod: "Manual",
        centroids: manualCentroids,
      })
      .then(() => {
        setHasInitialized(true); // Update initialization state
        fetchUpdatedPlot();
      })
      .catch((error) => {
        console.error(
          "There was an error initializing manual clustering!",
          error
        );
      });
  };

  const handleInitialize = (): void => {
    if (!hasGenDataset) {
      alert("Please generate a dataset first!");
      return;
    }
    axios
      .post("http://localhost:5000/initialize-clustering", {
        numClusters: numClusters,
        initMethod: selectedMethod,
      })
      .then(() => {
        setHasInitialized(true); // Update initialization state
        fetchUpdatedPlot();
      })
      .catch((error) => {
        console.error("There was an error initializing the clustering!", error);
      });
  };

  const handleStepThrough = (): void => {
    if (!hasInitialized || hasConverged) {
      alert("Please initialize clustering first!");
      return;
    }

    axios
      .post("http://localhost:5000/step-clustering", {
        numClusters: numClusters,
        initMethod: selectedMethod,
      })
      .then(() => {
        fetchUpdatedPlot();
      })
      .catch((error) => {
        console.error("There was an error performing the step-through!", error);
      });
  };

  const handleConverge = (): void => {
    if (!hasInitialized || hasConverged) {
      alert("Please initialize clustering first!");
      return;
    }
    axios
      .post("http://localhost:5000/converge-clustering")
      .then(() => {
        fetchUpdatedPlot();
        setHasConverged(true); // Update state to indicate convergence
      })
      .catch((error) => {
        console.error("There was an error running the convergence!", error);
      });
  };

  const fetchUpdatedPlot = (): void => {
    axios
      .get("http://localhost:5000/generate-plot", {
        responseType: "blob",
      })
      .then((res) => {
        const imageURL = URL.createObjectURL(res.data);
        setImageSrc(imageURL); // Update state with the new image source
      })
      .catch((error) => {
        console.error("There was an error fetching the updated plot!", error);
      });
  };

  const handleGenerateDataset = (): void => {
    axios
      .get("http://localhost:5000/generate-dataset", {
        params: {
          num_points: numPoints,
        },
        responseType: "blob",
      })
      .then((res) => {
        const imageURL = URL.createObjectURL(res.data);
        setImageSrc(imageURL); // Update state with the new image source
        setHasGenDataset(true);
        setHasInitialized(false); // Reset clustering state
        setHasConverged(false); // Reset convergence state
        setCentroidMessages([]); // Clear previous centroid messages
      })
      .catch((error) => {
        console.error("There was an error generating the dataset!", error);
      });
  };

  const handleReset = (): void => {
    setImageSrc(null); // Reset the image
    setHasGenDataset(false);
    setHasInitialized(false); // Reset initialization state
    setHasConverged(false); // Reset convergence state
    setNumClusters(3);
    setNumPoints(100);
    setSelectedMethod("Random");
    setCentroidMessages([]); // Clear centroid messages
  };

  return (
    <>
      <div className="app-container">
        {/* Plot Section */}
        <div className="plot-container">
          {imageSrc ? (
            <img
              src={imageSrc}
              alt="Generated Dataset Graph"
              className="plot"
              onClick={handlePlotClick}
            />
          ) : (
            <p className="pl-6 mt-6 italic">
              EMPTY PLOT
              <br />
              <hr />
              <br />
              Please click the "Generate Random Dataset" button to begin.
            </p>
          )}
          {/* Centroid Messages Section */}
          {centroidMessages.length > 0 && (
            <div className="centroid-messages-container">
              <h2 className="mb-4 text-lg font-bold">Selected Centroids:</h2>
              <ul className="centroid-message-list">
                {centroidMessages.map((message, index) => (
                  <li key={index} className="centroid-message-item">
                    {message}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Controls Section */}
        <div className="controls-container">
          <h1 className="text-4xl font-extrabold tracking-tight scroll-m-20 lg:text-5xl">
            KMeans Clustering Algorithm
        
          </h1>
      <h2 className="pb-2 mt-5 text-2xl  tracking-tight transition-colors border-b scroll-m-20 first:mt-1 italic"> By Adi Bhan </h2>
          <label
            className="text-2xl font-semibold tracking-tight scroll-m-20"
            htmlFor="numPoints"
          >
            Number of data points:
          </label>
          <Input
            min="10"
            max="1000"
            type="number"
            id="numPoints"
            name="numPoints"
            value={numPoints}
            onChange={(e) => setNumPoints(Number(e.target.value))}
          />

          <label
            className="text-2xl font-semibold tracking-tight scroll-m-20"
            htmlFor="numClusters"
          >
            Number of clusters:
          </label>
          <Input
            min="1"
            max="10"
            type="number"
            id="numClusters"
            name="numClusters"
            value={numClusters}
            onChange={(e) => setNumClusters(Number(e.target.value))}
          />
          <label
            className="text-2xl font-semibold tracking-tight scroll-m-20"
            htmlFor="initMethod"
          >
            Initialization method:
          </label>
          <DropdownMenu>
            <DropdownMenuTrigger className="dropdown-menu-trigger">
              {selectedMethod}
            </DropdownMenuTrigger>
            <DropdownMenuContent className="dropdown-menu-content">
              <DropdownMenuLabel>
                Select Initialization Method
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={() => handleSelect("Random")}>
                Random
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => handleSelect("Furthest First")}>
                Furthest First
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => handleSelect("KMeans++")}>
                KMeans++
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => handleSelect("Manual")}>
                Manual
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="button-container">
            <Alert
              triggerButton={
                <Button
                  className="button"
                  disabled={!hasGenDataset || hasInitialized}
                >
                  Initialize Clustering
                </Button>
              }
              title="Initialize Clustering"
              description="Are you sure you want to initialize the clustering? This action will reset any previous clustering steps."
              onConfirm={handleInitialize}
            />

            <Button
              onClick={handleStepThrough}
              className="button"
              disabled={!hasInitialized || hasConverged}
            >
              Step Through
            </Button>

            <Alert
              triggerButton={
                <Button
                  className="button"
                  disabled={!hasInitialized || hasConverged}
                >
                  Run to Convergence
                </Button>
              }
              title="Run to Convergence"
              description="This will run the entire clustering process until convergence. Continue?"
              onConfirm={handleConverge}
            />

            <Alert
              triggerButton={
                <Button className="button">Generate Random Dataset</Button>
              }
              title="Generate Random Dataset"
              description="This will generate a new random dataset. Continue?"
              onConfirm={handleGenerateDataset}
            />

            <Alert
              triggerButton={
                <Button className="button">Reset Algorithm</Button>
              }
              title="Reset Algorithm"
              description="This will reset the algorithm and dataset to their default state. Are you sure you want to proceed?"
              onConfirm={handleReset}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
