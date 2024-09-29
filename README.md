# KMeans Clustering Algorithm Visualizer

## Demo

A demo video is provided in the repository under the `assign-02.mp4` file. [Watch the Demo](./assign-02.mp4)

## Overview

This project is a visualizer for the KMeans clustering algorithm, built with a **ReactJS** frontend and a **Flask** backend. The backend uses powerful Python libraries like **Matplotlib**, **Pandas**, and **NumPy** to handle data processing and visualization. The app allows users to:
- Generate random datasets.
- Visualize clusters formed using different initialization methods.
- Step through the clustering process or run the algorithm to convergence.

## Key Features
- **Interactive Visuals**: Click on the graph to manually set centroids, or choose from pre-defined initialization methods like Random or KMeans++.
- **Multiple Initialization Methods**: Supports Random, Furthest First, KMeans++, and Manual.
- **Step-by-Step Clustering**: Step through each iteration of the algorithm to see how clusters evolve.
- **Automatic Convergence**: Run the algorithm to convergence with one click.

## Technologies Used
- **Frontend**: ReactJS, HTML, CSS
- **Backend**: Flask
- **Data Visualization**: Matplotlib
- **Data Handling**: Pandas, NumPy

## Installation

You can quickly set up the project using the provided `Makefile`.

### Prerequisites
- Python 3.8+
- Node.js and npm
- Make

### Steps

1. **Clone the repository**:
    ```bash
    git clone git@github.com:AdiBhan/kmeans-visualizer.git 
    cd kmeans-visualizer
    ```

2. **Install dependencies**:
    Run the following command to install both frontend and backend dependencies:
    ```bash
    make install
    ```

3. **Run the application**:
    After installation, use the following command to start the app:
    ```bash
    make run
    ```

    This will:
    - Start the Flask backend on `http://localhost:5000`
    - Start the React frontend on `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`.
2. Use the dropdown menu to select an initialization method (e.g., Random, KMeans++).
3. Generate a dataset by clicking the **Generate Random Dataset** button.
4. Click **Initialize Clustering** to start the algorithm.
5. Step through each iteration or run the algorithm to convergence.
6. View the clustering results on the generated graph.


## Folder Structure

