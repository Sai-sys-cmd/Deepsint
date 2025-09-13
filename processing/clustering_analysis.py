from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Set
import os, hashlib, json, time, asyncio
import base64
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class ProfileClusteringAnalysis:
    """
    Comprehensive clustering analysis for profile picture embeddings and metadata embeddings
    using both DBSCAN (auto-eps) and Agglomerative clustering approaches.
    """
    
    def __init__(self, pfp_embeddings: Dict, metadata_embeddings: Dict):
        """
        Initialize with profile picture and metadata embeddings.
        
        Args:
            pfp_embeddings: Dictionary mapping profile indices to PFP embeddings
            metadata_embeddings: Dictionary mapping profile indices to metadata embeddings
        """
        self.pfp_embeddings = pfp_embeddings
        self.metadata_embeddings = metadata_embeddings
        self.pfp_array = None
        self.metadata_array = None
        self.pfp_indices = None
        self.metadata_indices = None
        self.results = {}
        
        self._prepare_data()
    
    def _prepare_data(self):
        """Convert embeddings dictionaries to numpy arrays for clustering."""
        # Prepare PFP embeddings
        if self.pfp_embeddings:
            self.pfp_indices = list(self.pfp_embeddings.keys())
            pfp_list = []
            for idx in self.pfp_indices:
                embedding = self.pfp_embeddings[idx]
                # Handle nested list structure from Cohere
                if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                    embedding = embedding[0]
                pfp_list.append(embedding)
            self.pfp_array = np.array(pfp_list)
            print(f"PFP embeddings shape: {self.pfp_array.shape}")
        
        # Prepare metadata embeddings
        if self.metadata_embeddings:
            self.metadata_indices = list(self.metadata_embeddings.keys())
            meta_list = []
            for idx in self.metadata_indices:
                embedding = self.metadata_embeddings[idx]
                # Handle nested list structure from Cohere
                if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                    embedding = embedding[0]
                meta_list.append(embedding)
            self.metadata_array = np.array(meta_list)
            print(f"Metadata embeddings shape: {self.metadata_array.shape}")
    
    def calculate_optimal_eps(self, embeddings: np.ndarray, min_samples: int = 5) -> float:
        """
        Calculate optimal eps parameter for DBSCAN using the k-distance graph method.
        
        Args:
            embeddings: Embedding array
            min_samples: Minimum samples parameter for DBSCAN
            
        Returns:
            Optimal eps value
        """
        # Use cosine distance for high-dimensional embeddings
        distances = 1 - cosine_similarity(embeddings)
        
        # Find k-nearest neighbors
        neighbors = NearestNeighbors(n_neighbors=min_samples, metric='precomputed')
        neighbors_fit = neighbors.fit(distances)
        distances_knn, indices = neighbors_fit.kneighbors(distances)
        
        # Sort distances to k-th nearest neighbor
        distances_knn = np.sort(distances_knn[:, min_samples-1], axis=0)
        
        # Find the "elbow" point - simplified approach
        # Calculate the point of maximum curvature
        if len(distances_knn) > 10:
            # Use the point where the rate of change is maximum
            diffs = np.diff(distances_knn)
            second_diffs = np.diff(diffs)
            if len(second_diffs) > 0:
                elbow_idx = np.argmax(second_diffs) + 2
                optimal_eps = distances_knn[min(elbow_idx, len(distances_knn)-1)]
            else:
                optimal_eps = np.percentile(distances_knn, 90)
        else:
            optimal_eps = np.percentile(distances_knn, 90)
        
        return optimal_eps
    
    def dbscan_clustering(self, embeddings: np.ndarray, embedding_type: str, 
                         min_samples: int = 5) -> Dict:
        """
        Perform DBSCAN clustering with automatic eps calculation.
        
        Args:
            embeddings: Embedding array
            embedding_type: Type of embeddings ("pfp" or "metadata")
            min_samples: Minimum samples parameter
            
        Returns:
            Dictionary with clustering results
        """
        print(f"\nPerforming DBSCAN clustering for {embedding_type} embeddings...")
        
        # Calculate optimal eps
        optimal_eps = self.calculate_optimal_eps(embeddings, min_samples)
        print(f"Optimal eps for {embedding_type}: {optimal_eps:.4f}")
        
        # Use cosine distance for high-dimensional embeddings
        distances = 1 - cosine_similarity(embeddings)
        
        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=optimal_eps, min_samples=min_samples, metric='precomputed')
        cluster_labels = dbscan.fit_predict(distances)
        
        # Calculate metrics
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        results = {
            'method': 'DBSCAN',
            'embedding_type': embedding_type,
            'eps': optimal_eps,
            'min_samples': min_samples,
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'cluster_labels': cluster_labels,
            'silhouette_score': None,
            'calinski_harabasz_score': None,
            'davies_bouldin_score': None
        }
        
        # Calculate clustering metrics (only if we have more than 1 cluster)
        if n_clusters > 1 and n_clusters < len(embeddings):
            try:
                results['silhouette_score'] = silhouette_score(distances, cluster_labels, metric='precomputed')
                results['calinski_harabasz_score'] = calinski_harabasz_score(embeddings, cluster_labels)
                results['davies_bouldin_score'] = davies_bouldin_score(embeddings, cluster_labels)
            except Exception as e:
                print(f"Warning: Could not calculate some metrics: {e}")
        
        print(f"DBSCAN Results for {embedding_type}:")
        print(f"  - Number of clusters: {n_clusters}")
        print(f"  - Number of noise points: {n_noise}")
        print(f"  - Silhouette score: {results['silhouette_score']:.4f}" if results['silhouette_score'] else "  - Silhouette score: N/A")
        
        return results
    
    def agglomerative_clustering(self, embeddings: np.ndarray, embedding_type: str,
                               k_range: Tuple[int, int] = (2, 10)) -> Dict:
        """
        Perform Agglomerative clustering with different k values.
        
        Args:
            embeddings: Embedding array
            embedding_type: Type of embeddings ("pfp" or "metadata")
            k_range: Range of k values to try
            
        Returns:
            Dictionary with clustering results for different k values
        """
        print(f"\nPerforming Agglomerative clustering for {embedding_type} embeddings...")
        
        results = {
            'method': 'Agglomerative',
            'embedding_type': embedding_type,
            'k_results': {}
        }
        
        best_k = None
        best_score = -1
        
        min_k, max_k = k_range
        max_k = min(max_k, len(embeddings) - 1)  # Can't have more clusters than samples
        
        for k in range(min_k, max_k + 1):
            try:
                # Perform clustering
                agg_clustering = AgglomerativeClustering(
                    n_clusters=k,
                    linkage='ward'  # Ward linkage works well with Euclidean distance
                )
                cluster_labels = agg_clustering.fit_predict(embeddings)
                
                # Calculate metrics
                silhouette = silhouette_score(embeddings, cluster_labels)
                calinski_harabasz = calinski_harabasz_score(embeddings, cluster_labels)
                davies_bouldin = davies_bouldin_score(embeddings, cluster_labels)
                
                k_result = {
                    'k': k,
                    'cluster_labels': cluster_labels,
                    'silhouette_score': silhouette,
                    'calinski_harabasz_score': calinski_harabasz,
                    'davies_bouldin_score': davies_bouldin
                }
                
                results['k_results'][k] = k_result
                
                # Track best k based on silhouette score
                if silhouette > best_score:
                    best_score = silhouette
                    best_k = k
                
                print(f"  k={k}: Silhouette={silhouette:.4f}, CH={calinski_harabasz:.2f}, DB={davies_bouldin:.4f}")
                
            except Exception as e:
                print(f"  k={k}: Error - {e}")
        
        results['best_k'] = best_k
        results['best_score'] = best_score
        
        print(f"Best k for {embedding_type}: {best_k} (Silhouette score: {best_score:.4f})")
        
        return results
    
    def analyze_clusters(self, cluster_labels: np.ndarray, embeddings: np.ndarray, 
                        embedding_type: str, indices: List) -> Dict:
        """
        Analyze cluster characteristics and provide insights.
        
        Args:
            cluster_labels: Cluster assignments
            embeddings: Embedding array
            embedding_type: Type of embeddings
            indices: Original indices mapping
            
        Returns:
            Dictionary with cluster analysis
        """
        unique_labels = set(cluster_labels)
        cluster_analysis = {}
        
        for label in unique_labels:
            if label == -1:  # Noise points in DBSCAN
                cluster_name = "Noise"
            else:
                cluster_name = f"Cluster_{label}"
            
            mask = cluster_labels == label
            cluster_embeddings = embeddings[mask]
            cluster_indices = [indices[i] for i in range(len(indices)) if mask[i]]
            
            # Calculate cluster statistics
            cluster_size = len(cluster_embeddings)
            if cluster_size > 1:
                # Calculate intra-cluster similarity
                similarities = cosine_similarity(cluster_embeddings)
                avg_similarity = np.mean(similarities[np.triu_indices_from(similarities, k=1)])
                
                # Calculate cluster centroid
                centroid = np.mean(cluster_embeddings, axis=0)
            else:
                avg_similarity = 1.0
                centroid = cluster_embeddings[0] if cluster_size == 1 else None
            
            cluster_analysis[cluster_name] = {
                'label': label,
                'size': cluster_size,
                'indices': cluster_indices,
                'avg_intra_similarity': avg_similarity,
                'centroid': centroid
            }
        
        return cluster_analysis
    
    def visualize_clusters(self, embeddings: np.ndarray, cluster_labels: np.ndarray,
                          title: str, save_path: Optional[str] = None):
        """
        Visualize clusters using PCA for dimensionality reduction.
        
        Args:
            embeddings: Embedding array
            cluster_labels: Cluster assignments
            title: Plot title
            save_path: Optional path to save the plot
        """
        # Reduce dimensionality for visualization
        pca = PCA(n_components=2)
        embeddings_2d = pca.fit_transform(embeddings)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Get unique labels and colors
        unique_labels = set(cluster_labels)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
        
        for label, color in zip(unique_labels, colors):
            if label == -1:
                # Noise points (black)
                mask = cluster_labels == label
                plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                           c='black', marker='x', s=50, alpha=0.6, label='Noise')
            else:
                mask = cluster_labels == label
                plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                           c=[color], s=60, alpha=0.8, label=f'Cluster {label}')
        
        plt.title(title)
        plt.xlabel(f'First Principal Component (explained variance: {pca.explained_variance_ratio_[0]:.2%})')
        plt.ylabel(f'Second Principal Component (explained variance: {pca.explained_variance_ratio_[1]:.2%})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def run_complete_analysis(self, save_visualizations: bool = True) -> Dict:
        """
        Run complete clustering analysis for both embedding types.
        
        Args:
            save_visualizations: Whether to save visualization plots
            
        Returns:
            Complete analysis results
        """
        print("=" * 60)
        print("COMPREHENSIVE CLUSTERING ANALYSIS")
        print("=" * 60)
        
        all_results = {
            'pfp_results': {},
            'metadata_results': {},
            'summary': {}
        }
        
        # Analyze PFP embeddings
        if self.pfp_array is not None and len(self.pfp_array) > 1:
            print(f"\nAnalyzing {len(self.pfp_array)} profile picture embeddings...")
            
            # DBSCAN clustering
            pfp_dbscan = self.dbscan_clustering(self.pfp_array, "pfp")
            all_results['pfp_results']['dbscan'] = pfp_dbscan
            
            # Agglomerative clustering
            pfp_agg = self.agglomerative_clustering(self.pfp_array, "pfp")
            all_results['pfp_results']['agglomerative'] = pfp_agg
            
            # Cluster analysis for best results
            if pfp_dbscan['n_clusters'] > 0:
                pfp_dbscan_analysis = self.analyze_clusters(
                    pfp_dbscan['cluster_labels'], self.pfp_array, "pfp", self.pfp_indices
                )
                all_results['pfp_results']['dbscan_analysis'] = pfp_dbscan_analysis
            
            if pfp_agg['best_k']:
                best_agg_labels = pfp_agg['k_results'][pfp_agg['best_k']]['cluster_labels']
                pfp_agg_analysis = self.analyze_clusters(
                    best_agg_labels, self.pfp_array, "pfp", self.pfp_indices
                )
                all_results['pfp_results']['agglomerative_analysis'] = pfp_agg_analysis
            
            # Visualizations
            if save_visualizations:
                if pfp_dbscan['n_clusters'] > 0:
                    self.visualize_clusters(
                        self.pfp_array, pfp_dbscan['cluster_labels'],
                        f"PFP Embeddings - DBSCAN Clustering (eps={pfp_dbscan['eps']:.4f})",
                        "pfp_dbscan_clusters.png"
                    )
                
                if pfp_agg['best_k']:
                    self.visualize_clusters(
                        self.pfp_array, best_agg_labels,
                        f"PFP Embeddings - Agglomerative Clustering (k={pfp_agg['best_k']})",
                        "pfp_agglomerative_clusters.png"
                    )
        
        # Analyze metadata embeddings
        if self.metadata_array is not None and len(self.metadata_array) > 1:
            print(f"\nAnalyzing {len(self.metadata_array)} metadata embeddings...")
            
            # DBSCAN clustering
            meta_dbscan = self.dbscan_clustering(self.metadata_array, "metadata")
            all_results['metadata_results']['dbscan'] = meta_dbscan
            
            # Agglomerative clustering
            meta_agg = self.agglomerative_clustering(self.metadata_array, "metadata")
            all_results['metadata_results']['agglomerative'] = meta_agg
            
            # Cluster analysis for best results
            if meta_dbscan['n_clusters'] > 0:
                meta_dbscan_analysis = self.analyze_clusters(
                    meta_dbscan['cluster_labels'], self.metadata_array, "metadata", self.metadata_indices
                )
                all_results['metadata_results']['dbscan_analysis'] = meta_dbscan_analysis
            
            if meta_agg['best_k']:
                best_agg_labels = meta_agg['k_results'][meta_agg['best_k']]['cluster_labels']
                meta_agg_analysis = self.analyze_clusters(
                    best_agg_labels, self.metadata_array, "metadata", self.metadata_indices
                )
                all_results['metadata_results']['agglomerative_analysis'] = meta_agg_analysis
            
            # Visualizations
            if save_visualizations:
                if meta_dbscan['n_clusters'] > 0:
                    self.visualize_clusters(
                        self.metadata_array, meta_dbscan['cluster_labels'],
                        f"Metadata Embeddings - DBSCAN Clustering (eps={meta_dbscan['eps']:.4f})",
                        "metadata_dbscan_clusters.png"
                    )
                
                if meta_agg['best_k']:
                    self.visualize_clusters(
                        self.metadata_array, best_agg_labels,
                        f"Metadata Embeddings - Agglomerative Clustering (k={meta_agg['best_k']})",
                        "metadata_agglomerative_clusters.png"
                    )
        
        # Generate summary
        summary = self._generate_summary(all_results)
        all_results['summary'] = summary
        
        return all_results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate a summary of all clustering results."""
        summary = {
            'pfp_summary': {},
            'metadata_summary': {},
            'recommendations': []
        }
        
        # PFP summary
        if 'pfp_results' in results and results['pfp_results']:
            pfp_res = results['pfp_results']
            summary['pfp_summary'] = {
                'total_profiles': len(self.pfp_array) if self.pfp_array is not None else 0,
                'dbscan_clusters': pfp_res.get('dbscan', {}).get('n_clusters', 0),
                'dbscan_noise': pfp_res.get('dbscan', {}).get('n_noise', 0),
                'agglomerative_best_k': pfp_res.get('agglomerative', {}).get('best_k', 0),
                'agglomerative_best_score': pfp_res.get('agglomerative', {}).get('best_score', 0)
            }
        
        # Metadata summary
        if 'metadata_results' in results and results['metadata_results']:
            meta_res = results['metadata_results']
            summary['metadata_summary'] = {
                'total_profiles': len(self.metadata_array) if self.metadata_array is not None else 0,
                'dbscan_clusters': meta_res.get('dbscan', {}).get('n_clusters', 0),
                'dbscan_noise': meta_res.get('dbscan', {}).get('n_noise', 0),
                'agglomerative_best_k': meta_res.get('agglomerative', {}).get('best_k', 0),
                'agglomerative_best_score': meta_res.get('agglomerative', {}).get('best_score', 0)
            }
        
        # Generate recommendations
        recommendations = []
        
        if summary['pfp_summary'].get('dbscan_clusters', 0) > 0:
            recommendations.append("PFP embeddings show clear clustering structure with DBSCAN")
        
        if summary['metadata_summary'].get('dbscan_clusters', 0) > 0:
            recommendations.append("Metadata embeddings show clear clustering structure with DBSCAN")
        
        if summary['pfp_summary'].get('agglomerative_best_score', 0) > 0.5:
            recommendations.append("Agglomerative clustering works well for PFP embeddings")
        
        if summary['metadata_summary'].get('agglomerative_best_score', 0) > 0.5:
            recommendations.append("Agglomerative clustering works well for metadata embeddings")
        
        summary['recommendations'] = recommendations
        
        return summary
    
    def save_results(self, results: Dict, filename: str = "clustering_results.json"):
        """Save clustering results to JSON file."""
        # Convert numpy arrays to lists for JSON serialization
        json_results = self._convert_for_json(results)
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"Results saved to {filename}")
    
    def _convert_for_json(self, obj):
        """Convert numpy arrays and other non-serializable objects for JSON."""
        if isinstance(obj, dict):
            return {key: self._convert_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return obj


def load_embeddings_from_profiler(json_file_path: str):
    """
    Load embeddings generated by the profiler.py script.
    This is a helper function to integrate with the existing profiler.
    """
    # Import the profiler function
    from profiler import calculate_cohere_embeddings
    
    print("Loading embeddings from profiler...")
    pfp_embeddings, metadata_embeddings = calculate_cohere_embeddings(json_file_path)
    
    return pfp_embeddings, metadata_embeddings


def main():
    """Main function to run the complete clustering analysis."""
    # Load embeddings
    json_file_path = "generic_scrape_results.json"
    
    try:
        pfp_embeddings, metadata_embeddings = load_embeddings_from_profiler(json_file_path)
        
        # Initialize clustering analysis
        analyzer = ProfileClusteringAnalysis(pfp_embeddings, metadata_embeddings)
        
        # Run complete analysis
        results = analyzer.run_complete_analysis(save_visualizations=True)
        
        # Save results
        analyzer.save_results(results)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        
        summary = results['summary']
        
        if summary.get('pfp_summary'):
            pfp_sum = summary['pfp_summary']
            print(f"\nProfile Picture Embeddings:")
            print(f"  - Total profiles: {pfp_sum['total_profiles']}")
            print(f"  - DBSCAN clusters: {pfp_sum['dbscan_clusters']} (noise: {pfp_sum['dbscan_noise']})")
            print(f"  - Best Agglomerative k: {pfp_sum['agglomerative_best_k']} (score: {pfp_sum['agglomerative_best_score']:.4f})")
        
        if summary.get('metadata_summary'):
            meta_sum = summary['metadata_summary']
            print(f"\nMetadata Embeddings:")
            print(f"  - Total profiles: {meta_sum['total_profiles']}")
            print(f"  - DBSCAN clusters: {meta_sum['dbscan_clusters']} (noise: {meta_sum['dbscan_noise']})")
            print(f"  - Best Agglomerative k: {meta_sum['agglomerative_best_k']} (score: {meta_sum['agglomerative_best_score']:.4f})")
        
        if summary.get('recommendations'):
            print(f"\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        print("\nAnalysis complete! Check the generated visualizations and clustering_results.json for detailed results.")
        
    except Exception as e:
        print(f"Error running analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
