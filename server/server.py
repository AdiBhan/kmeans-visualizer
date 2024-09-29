from io import BytesIO
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Global variables to maintain state
global_data = {
    'dataset': None,
    'centroids': None,
    'assignments': None
}




def generate_random_dataset(num_points=100, x_range=(0, 100), y_range=(0, 100)):
    
    # generate_random_dataset generates a random dataset with specified number of points and ranges for x and y coordinates
    data = {
        'x': [random.uniform(*x_range) for _ in range(num_points)],
        'y': [random.uniform(*y_range) for _ in range(num_points)]
    }
    return pd.DataFrame(data)

# Function to calculate the distance between two points


def euclidean_distance(point1, point2):
    
    # euclidean_distance: Helper function to calculate the distance between two points
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5



def initialize_centroids(dataset, k, method):
    
    # initialize_centroids initializes centroids based on the specified method
    
    data_list = dataset.values.tolist()
    

    if method == 'Random':
        return random.sample(data_list, k)
    elif method == 'Furthest First':
        return furthest_first_init(data_list, k)
    elif method == 'KMeans++':
        return kmeans_plus_plus_init(data_list, k)
    elif method == 'Manual':  
        # If manual centroids are being passed, they are already in the global_data
        return global_data['centroids']  # Assuming centroids are already provided
    else:
        raise ValueError(f"Invalid initialization method: {method}")
    


def furthest_first_init(dataset, k):
    # furthest_first_init initializes centroids using Furthest First algorithm
    centroids = [random.choice(dataset)]
    
    # Calculate the squared distances from each data point to the current centroids
    while len(centroids) < k:
        
        # Calculate the squared distances from each data point to the current centroids
        distances = [min(euclidean_distance(point, c)
                         for c in centroids) for point in dataset]
        next_centroid = dataset[distances.index(max(distances))]
        centroids.append(next_centroid)
    return centroids


def kmeans_plus_plus_init(dataset, k):
    # kmeans_plus_plus_init initializes centroids using KMeans++ algorithm

    centroids = [random.choice(dataset)]

    # Choose the first centroid randomly
    for _ in range(1, k):

        # Calculate the squared distances from each data point to the current centroids
        distances = [min(euclidean_distance(point, c)
                         for c in centroids)**2 for point in dataset]
        total_distance = sum(distances)
        probabilities = [d / total_distance for d in distances]
        next_centroid = random.choices(dataset, weights=probabilities)[0]
        centroids.append(next_centroid)
    return centroids


def assign_clusters(dataset, centroids):
    #  assign_clusters assigns each data point to the nearest centroid by calculating the Euclidean distance to each centroid

    # Iterate over each data point and find the nearest centroid
    
    print(dataset)
    print(centroids)
    assignments = []

    for _, point in dataset.iterrows():
        distances = [euclidean_distance(point, centroid) for centroid in centroids]
        assignments.append(distances.index(min(distances)))

    # Return the assignments as a pandas Series for proper indexing
    return pd.Series(assignments)


def update_centroids(dataset, assignments, k):

    # update_centroids updates centroids by calculating the mean of points in each cluster
    new_centroids = []

    # Iterate over each cluster ID and calculate the new centroid
    for cluster_id in range(k):
        # Use `.loc` to filter dataset based on cluster assignments
        cluster_points = dataset.loc[assignments == cluster_id]

        # Calculate the mean of the points in the cluster to update the centroid
        if not cluster_points.empty:
            new_centroid = cluster_points.mean().tolist()
        # If the cluster is empty, reinitialize it with a random point from the dataset
        else:
            new_centroid = random.choice(dataset.values.tolist())
        new_centroids.append(new_centroid)

    return new_centroids

# Endpoint for generating dataset and graph


@app.route('/generate-dataset', methods=['GET'])
def generate_dataset():
    # generate_dataset generates a random dataset based on the specified number of points and returns the dataset as a JSON response

    # Get number of points from query, default is 100
    num_points = int(request.args.get('num_points', 100))
    dataset = generate_random_dataset(num_points=num_points)
    global_data['dataset'] = dataset
    global_data['centroids'] = None
    global_data['assignments'] = None

    # Create scatter plot using matplotlib
    plt.figure(figsize=(6, 6))
    plt.scatter(dataset['x'], dataset['y'], color='blue')
    plt.title('Random Dataset Scatter Plot')
    plt.xlabel('X')
    plt.ylabel('Y')

    # Save the plot to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Send the image as a response
    return send_file(buf, mimetype='image/png')


@app.route('/generate-plot', methods=['GET'])
# Endpoint for generating plot based on the current clustering state
def generate_plot():
    # generate_plot generates the plot based on the current clustering state and returns the plot as an image
    # Assumes global_data contains the dataset, centroids, and assignments variables
    # Returns the image as a response if clustering is initialized, otherwise returns an error message and status code 400
    dataset = global_data['dataset']
    centroids = global_data['centroids']
    assignments = global_data['assignments']

    if dataset is None or centroids is None or assignments is None:
        return jsonify({"error": "Clustering is not initialized"}), 400

    # Create scatter plot using matplotlib
    plt.figure(figsize=(6, 6))
    # Plot data points colored by their cluster assignment
    for cluster_id in range(len(centroids)):
        cluster_points = dataset[pd.Series(assignments) == cluster_id]
        plt.scatter(cluster_points['x'], cluster_points['y'], label=f'Cluster {cluster_id + 1}')


    # Plot centroids
    centroid_array = np.array(centroids)
    plt.scatter(centroid_array[:, 0], centroid_array[:, 1],
                color='red', marker='X', s=100, label='Centroids')

    plt.title('K-Means Clustering')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()

    # Save the plot to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Send the image as a response
    return send_file(buf, mimetype='image/png')


@app.route('/initialize-clustering', methods=['POST'])
# Endpoint for initializing clustering
def initialize_clustering():
    # initialize_clustering initializes the clustering with the specified number of clusters and initialization method
    # Returns the initialized clustering state as a JSON response if successful, otherwise returns an error message and status code 400

    data = request.json
    num_clusters = data.get('numClusters')
    init_method = data.get('initMethod')
    points = data.get('centroids', None)  # This is used for manual initialization
    
    # Debugging logs
    print(f"Received numClusters: {num_clusters}, initMethod: {init_method}, centroids: {points}")
    
    if global_data['dataset'] is None:
        return jsonify({"error": "No dataset found"}), 400

    if init_method == 'Manual' and points is not None:
        # Use manual centroids
        centroids = points
    else:
        # Use automatic initialization methods (Random, KMeans++, etc.)
        centroids = initialize_centroids(global_data['dataset'], num_clusters, init_method)

    if centroids is None:
        return jsonify({"error": "Centroid initialization failed"}), 500
    
    global_data['centroids'] = centroids
    global_data['assignments'] = assign_clusters(global_data['dataset'], centroids)
    
    return jsonify({
        "message": f"Clustering initialized with {num_clusters} clusters using {init_method} initialization.",
        "centroids": centroids,
    })
# Endpoint for performing a single step of clustering


@app.route('/step-clustering', methods=['POST'])
def step_clustering():
    # step_clustering performs a single step of clustering and returns the updated clustering state as a JSON response
    # Assumes global_data contains the dataset, centroids, and assignments variables
    # Returns the updated clustering state as a JSON response if clustering is initialized, otherwise returns an error message and status code 400

    data = request.json
    num_clusters = data.get('numClusters')
    init_method = data.get('initMethod')
    manual_centroids = data.get('centroids', None)  # This is used for manual initialization
    dataset = global_data['dataset']

    # Ensure the dataset is available
    if dataset is None:
        return jsonify({"error": "No dataset found"}), 400

    # If manual centroids are provided, use them
    if init_method == 'Manual' and manual_centroids is not None:
        if len(manual_centroids) != num_clusters:
            return jsonify({"error": f"Expected {num_clusters} centroids, but got {len(manual_centroids)}"}), 400
        centroids = manual_centroids
    else:
        # Initialize centroids using the selected method (Random, KMeans++, Furthest First)
        centroids = initialize_centroids(dataset, num_clusters, init_method)

    # Assign clusters based on initialized centroids
    global_data['centroids'] = centroids
    global_data['assignments'] = assign_clusters(dataset, centroids)

    # Return the initialized centroids as a response
    return jsonify({
        "message": f"Clustering initialized with {num_clusters} clusters using {init_method} initialization.",
        "centroids": centroids,
    })
# Endpoint for running clustering until convergence


@app.route('/converge-clustering', methods=['POST'])
def converge_clustering():
    # converge_clustering runs clustering until convergence and returns the final clustering state as a JSON response
    # Assumes global_data contains the dataset, centroids, and assignments variables
    # Returns the final clustering state as a JSON response if clustering is initialized, otherwise returns an error message and status code 400

    dataset = global_data['dataset']
    centroids = global_data['centroids']
    assignments = global_data['assignments']

    # Check if dataset and centroids are available
    if dataset is None or centroids is None or assignments is None:
        return jsonify({"error": "Clustering is not initialized"}), 400

    # Run clustering until convergence
    while True:
        # Perform a single step of clustering
        new_centroids = update_centroids(
            dataset, pd.Series(assignments), len(centroids))

        # Check for convergence
        if new_centroids == centroids:
            break

        centroids = new_centroids
        assignments = assign_clusters(dataset, centroids)

    global_data['centroids'] = centroids
    global_data['assignments'] = assignments

    # Return the final clustering state as a JSON response
    return jsonify({
        "message": "Clustering has converged.",
        "centroids": centroids,
    })


if __name__ == '__main__':
    app.run(debug=True)
