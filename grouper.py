#!/usr/bin/env python3
"""
grouper.py - Group and cluster documents by keywords and topics

This module provides multiple state-of-the-art methods for document clustering,
keyword extraction, and topic analysis using free, open-source libraries.
"""

import os
import re
import json
import logging
import argparse
import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Union
from collections import Counter, defaultdict
import pickle

import pandas as pd
import numpy as np
from tqdm import tqdm

# Core ML libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# Advanced topic modeling
try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    import umap
    ADVANCED_MODELS_AVAILABLE = True
except ImportError:
    ADVANCED_MODELS_AVAILABLE = False
    warnings.warn("Advanced models (BERTopic, SentenceTransformers) not available. Using basic methods only.")

# Text processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from wordcloud import WordCloud

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

def setup_logging(log_dir: str = "logs") -> None:
    """Set up logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/grouper.log"),
            logging.StreamHandler()
        ]
    )

def download_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        # Try to use the data, download if not available
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logging.info("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt_tab', quiet=True)

class TextPreprocessor:
    """Advanced text preprocessing for document analysis."""
    
    def __init__(self, language: str = 'english'):
        """
        Initialize text preprocessor.
        
        Args:
            language: Language for stopwords and stemming
        """
        download_nltk_data()
        
        self.language = language
        self.stop_words = set(stopwords.words(language))
        
        # Add domain-specific stopwords
        self.stop_words.update({
            'cms', 'hospital', 'medicare', 'medicaid', 'program', 'rule', 'proposed',
            'comment', 'attachment', 'pdf', 'page', 'break', 'would', 'could', 'should',
            'also', 'however', 'therefore', 'additionally', 'furthermore', 'moreover',
            'th', 'st', 'nd', 'rd', 'et', 'al', 'etc', 'ie', 'eg', 'vs', 'inc',
            'llc', 'ltd', 'corp', 'co', 'dept', 'department', 'administration'
        })
        
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove page breaks and OCR artifacts
        text = re.sub(r'--- PAGE BREAK ---', ' ', text)
        text = re.sub(r'\[OCR [^]]+\]', ' ', text)
        
        # Remove URLs, emails, and file paths
        text = re.sub(r'http[s]?://\S+', ' ', text)
        text = re.sub(r'\S+@\S+\.\S+', ' ', text)
        text = re.sub(r'[A-Za-z]:\\[\w\\.\\]+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\-.,;:!?()]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove very short and very long words (likely artifacts)
        words = text.split()
        words = [w for w in words if 2 <= len(w) <= 25]
        
        return ' '.join(words).strip().lower()
    
    def extract_keywords_tfidf(self, texts: List[str], max_features: int = 100, 
                               min_df: int = 1, max_df: float = 0.95) -> List[str]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            texts: List of text documents
            max_features: Maximum number of features
            min_df: Minimum document frequency
            max_df: Maximum document frequency (proportion)
            
        Returns:
            List of top keywords
        """
        cleaned_texts = [self.clean_text(text) for text in texts]
        
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            stop_words=list(self.stop_words),
            ngram_range=(1, 2),  # Include bigrams
            lowercase=True
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Sort by score
            score_pairs = [(score, feature) for score, feature in zip(mean_scores, feature_names)]
            score_pairs.sort(reverse=True)
            
            return [feature for score, feature in score_pairs[:max_features]]
            
        except Exception as e:
            logging.warning(f"TF-IDF keyword extraction failed: {e}")
            return []
    
    def extract_keywords_frequency(self, texts: List[str], top_n: int = 50) -> List[str]:
        """
        Extract keywords using frequency analysis.
        
        Args:
            texts: List of text documents
            top_n: Number of top keywords to return
            
        Returns:
            List of top keywords by frequency
        """
        all_words = []
        
        for text in texts:
            cleaned = self.clean_text(text)
            words = word_tokenize(cleaned)
            
            # Filter out stopwords and short words
            words = [w for w in words if w.lower() not in self.stop_words and len(w) > 3]
            all_words.extend(words)
        
        # Count frequencies
        word_freq = Counter(all_words)
        
        return [word for word, freq in word_freq.most_common(top_n)]


class DocumentClusterer:
    """Advanced document clustering using multiple methods."""
    
    def __init__(self, preprocessor: TextPreprocessor):
        """
        Initialize document clusterer.
        
        Args:
            preprocessor: Text preprocessor instance
        """
        self.preprocessor = preprocessor
        self.models = {}
        self.vectorizers = {}
    
    def cluster_tfidf_kmeans(self, texts: List[str], n_clusters: int = 5, 
                           max_features: int = 1000) -> Tuple[List[int], Dict[str, Any]]:
        """
        Cluster documents using TF-IDF + KMeans.
        
        Args:
            texts: List of text documents
            n_clusters: Number of clusters
            max_features: Maximum TF-IDF features
            
        Returns:
            Tuple of (cluster_labels, metadata)
        """
        logging.info(f"Clustering {len(texts)} documents using TF-IDF + KMeans (k={n_clusters})")
        
        # Preprocess texts
        cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=2,
            max_df=0.8,
            stop_words=list(self.preprocessor.stop_words),
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
        
        # KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(tfidf_matrix, cluster_labels)
        
        # Get top terms for each cluster
        feature_names = vectorizer.get_feature_names_out()
        cluster_centers = kmeans.cluster_centers_
        
        cluster_terms = {}
        for i in range(n_clusters):
            top_indices = cluster_centers[i].argsort()[-10:][::-1]
            cluster_terms[i] = [feature_names[idx] for idx in top_indices]
        
        # Store models for later use
        self.models['tfidf_kmeans'] = kmeans
        self.vectorizers['tfidf_kmeans'] = vectorizer
        
        metadata = {
            'method': 'tfidf_kmeans',
            'n_clusters': n_clusters,
            'silhouette_score': silhouette_avg,
            'cluster_terms': cluster_terms,
            'feature_count': tfidf_matrix.shape[1]
        }
        
        logging.info(f"TF-IDF + KMeans clustering complete. Silhouette score: {silhouette_avg:.3f}")
        
        return cluster_labels.tolist(), metadata
    
    def cluster_bertopic(self, texts: List[str], min_topic_size: int = 2) -> Tuple[List[int], Dict[str, Any]]:
        """
        Cluster documents using BERTopic.
        
        Args:
            texts: List of text documents
            min_topic_size: Minimum size for a topic
            
        Returns:
            Tuple of (cluster_labels, metadata)
        """
        if not ADVANCED_MODELS_AVAILABLE:
            logging.error("BERTopic not available. Please install: pip install bertopic sentence-transformers")
            return [], {}
        
        logging.info(f"Clustering {len(texts)} documents using BERTopic")
        
        # Preprocess texts
        cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
        
        # Initialize BERTopic with optimal settings for small datasets
        topic_model = BERTopic(
            embedding_model='all-MiniLM-L6-v2',  # Fast, good quality embeddings
            min_topic_size=min_topic_size,
            nr_topics='auto',
            calculate_probabilities=True,
            verbose=False
        )
        
        # Fit model and get topics
        try:
            topics, probabilities = topic_model.fit_transform(cleaned_texts)
            
            # Get topic information
            topic_info = topic_model.get_topic_info()
            
            # Get representative words for each topic
            topic_words = {}
            for topic_id in topic_info['Topic'].unique():
                if topic_id != -1:  # Skip outlier topic
                    words = topic_model.get_topic(topic_id)
                    topic_words[topic_id] = [word for word, score in words[:10]]
            
            # Store model for later use
            self.models['bertopic'] = topic_model
            
            metadata = {
                'method': 'bertopic',
                'n_topics': len(topic_info) - 1,  # Exclude outlier topic
                'topic_words': topic_words,
                'topic_info': topic_info.to_dict('records'),
                'model_info': {
                    'embedding_model': 'all-MiniLM-L6-v2',
                    'min_topic_size': min_topic_size
                }
            }
            
            logging.info(f"BERTopic clustering complete. Found {len(topic_info) - 1} topics")
            
            return topics, metadata
            
        except Exception as e:
            logging.error(f"BERTopic clustering failed: {e}")
            return [], {}
    
    def cluster_lda(self, texts: List[str], n_topics: int = 5, 
                   max_features: int = 1000) -> Tuple[List[int], Dict[str, Any]]:
        """
        Cluster documents using Latent Dirichlet Allocation (LDA).
        
        Args:
            texts: List of text documents
            n_topics: Number of topics
            max_features: Maximum features for vectorization
            
        Returns:
            Tuple of (cluster_labels, metadata)
        """
        logging.info(f"Clustering {len(texts)} documents using LDA (topics={n_topics})")
        
        # Preprocess texts
        cleaned_texts = [self.preprocessor.clean_text(text) for text in texts]
        
        # Use CountVectorizer for LDA (works better than TF-IDF)
        vectorizer = CountVectorizer(
            max_features=max_features,
            min_df=2,
            max_df=0.8,
            stop_words=list(self.preprocessor.stop_words),
            ngram_range=(1, 1)  # LDA works better with unigrams
        )
        
        count_matrix = vectorizer.fit_transform(cleaned_texts)
        
        # LDA model
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=100,
            learning_method='batch'
        )
        
        lda.fit(count_matrix)
        
        # Get dominant topic for each document
        doc_topic_matrix = lda.transform(count_matrix)
        cluster_labels = np.argmax(doc_topic_matrix, axis=1)
        
        # Get top words for each topic
        feature_names = vectorizer.get_feature_names_out()
        topic_words = {}
        
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            topic_words[topic_idx] = [feature_names[i] for i in top_words_idx]
        
        # Store models
        self.models['lda'] = lda
        self.vectorizers['lda'] = vectorizer
        
        # Calculate perplexity (lower is better for LDA)
        perplexity = lda.perplexity(count_matrix)
        
        metadata = {
            'method': 'lda',
            'n_topics': n_topics,
            'perplexity': perplexity,
            'topic_words': topic_words,
            'feature_count': count_matrix.shape[1]
        }
        
        logging.info(f"LDA clustering complete. Perplexity: {perplexity:.3f}")
        
        return cluster_labels.tolist(), metadata


class DocumentGrouper:
    """Main class for document grouping and analysis."""
    
    def __init__(self, text_dir: str = "text", csv_path: str = "input/comment_links.csv"):
        """
        Initialize document grouper.
        
        Args:
            text_dir: Directory containing extracted text files
            csv_path: Path to original CSV with metadata
        """
        self.text_dir = text_dir
        self.csv_path = csv_path
        self.preprocessor = TextPreprocessor()
        self.clusterer = DocumentClusterer(self.preprocessor)
        
        self.documents = []
        self.metadata = []
        self.clusters = {}
        
    def load_documents(self) -> int:
        """
        Load all text documents and metadata.
        
        Returns:
            Number of documents loaded
        """
        logging.info(f"Loading documents from {self.text_dir}")
        
        # Load source metadata if available
        source_metadata = {}
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                for _, row in df.iterrows():
                    doc_id = str(row['Document ID']).strip()
                    source_metadata[doc_id] = {
                        'organization': str(row.get('Organization Name', '')).strip(),
                        'category': str(row.get('Category', '')).strip(),
                        'source_url': str(row.get('Attachment Files', '')).strip(),
                        'comment': str(row.get('Comment', '')).strip()
                    }
                logging.info(f"Loaded metadata for {len(source_metadata)} documents from CSV")
            except Exception as e:
                logging.warning(f"Could not load CSV metadata: {e}")
        
        # Load text files
        text_files = list(Path(self.text_dir).glob("*.txt"))
        
        if not text_files:
            logging.warning(f"No text files found in {self.text_dir}")
            return 0
        
        for text_file in tqdm(text_files, desc="Loading documents"):
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = text_file.name
                document_id = self._extract_document_id(filename)
                
                # Get metadata
                doc_metadata = source_metadata.get(document_id, {})
                
                self.documents.append(content)
                self.metadata.append({
                    'filename': filename,
                    'document_id': document_id,
                    'organization': doc_metadata.get('organization', ''),
                    'category': doc_metadata.get('category', ''),
                    'source_url': doc_metadata.get('source_url', ''),
                    'character_count': len(content),
                    'word_count': len(content.split()),
                    'file_path': str(text_file)
                })
                
            except Exception as e:
                logging.warning(f"Could not load {text_file}: {e}")
        
        logging.info(f"Loaded {len(self.documents)} documents")
        return len(self.documents)
    
    def _extract_document_id(self, filename: str) -> str:
        """Extract document ID from filename."""
        match = re.search(r'(CMS-\d{4}-\d{4}-\d{4})', filename)
        return match.group(1) if match else Path(filename).stem
    
    def analyze_documents(self, method: str = 'tfidf_kmeans', **kwargs) -> Dict[str, Any]:
        """
        Analyze and group documents using specified method.
        
        Args:
            method: Clustering method ('tfidf_kmeans', 'bertopic', 'lda')
            **kwargs: Additional parameters for clustering method
            
        Returns:
            Analysis results
        """
        if not self.documents:
            raise ValueError("No documents loaded. Call load_documents() first.")
        
        logging.info(f"Analyzing {len(self.documents)} documents using {method}")
        
        # Determine optimal number of clusters if not specified
        n_docs = len(self.documents)
        if method in ['tfidf_kmeans', 'lda'] and 'n_clusters' not in kwargs and 'n_topics' not in kwargs:
            # Use heuristic: sqrt(n_docs/2) but between 3 and 10
            optimal_k = max(3, min(10, int(np.sqrt(n_docs / 2))))
            if method == 'tfidf_kmeans':
                kwargs['n_clusters'] = optimal_k
            else:  # lda
                kwargs['n_topics'] = optimal_k
            logging.info(f"Auto-selected {optimal_k} clusters/topics for {n_docs} documents")
        
        # Perform clustering
        if method == 'tfidf_kmeans':
            cluster_labels, metadata = self.clusterer.cluster_tfidf_kmeans(self.documents, **kwargs)
        elif method == 'bertopic':
            cluster_labels, metadata = self.clusterer.cluster_bertopic(self.documents, **kwargs)
        elif method == 'lda':
            cluster_labels, metadata = self.clusterer.cluster_lda(self.documents, **kwargs)
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        if not cluster_labels:
            raise RuntimeError(f"Clustering failed for method: {method}")
        
        # Extract global keywords
        global_keywords_tfidf = self.preprocessor.extract_keywords_tfidf(self.documents, max_features=50)
        global_keywords_freq = self.preprocessor.extract_keywords_frequency(self.documents, top_n=30)
        
        # Organize results
        results = {
            'method': method,
            'metadata': metadata,
            'global_keywords': {
                'tfidf': global_keywords_tfidf,
                'frequency': global_keywords_freq
            },
            'documents': [],
            'clusters': defaultdict(list),
            'cluster_summaries': {}
        }
        
        # Process each document
        for i, (doc, meta, cluster_label) in enumerate(zip(self.documents, self.metadata, cluster_labels)):
            # Extract document-specific keywords (use frequency for single docs to avoid TF-IDF issues)
            doc_keywords_tfidf = self.preprocessor.extract_keywords_frequency([doc], top_n=10)
            doc_keywords_freq = self.preprocessor.extract_keywords_frequency([doc], top_n=10)
            
            # Create document summary (first 500 characters)
            clean_doc = self.preprocessor.clean_text(doc)
            summary = clean_doc[:500] + "..." if len(clean_doc) > 500 else clean_doc
            
            doc_result = {
                **meta,
                'cluster_label': cluster_label,
                'keywords_tfidf': doc_keywords_tfidf,
                'keywords_frequency': doc_keywords_freq,
                'summary': summary
            }
            
            results['documents'].append(doc_result)
            results['clusters'][cluster_label].append(doc_result)
        
        # Create cluster summaries
        for cluster_id, cluster_docs in results['clusters'].items():
            cluster_texts = [self.documents[i] for i, meta in enumerate(self.metadata) 
                           if cluster_labels[i] == cluster_id]
            
            cluster_keywords_tfidf = self.preprocessor.extract_keywords_tfidf(cluster_texts, max_features=15)
            cluster_keywords_freq = self.preprocessor.extract_keywords_frequency(cluster_texts, top_n=15)
            
            # Get most common organizations and categories
            orgs = [doc['organization'] for doc in cluster_docs if doc['organization']]
            categories = [doc['category'] for doc in cluster_docs if doc['category']]
            
            org_counts = Counter(orgs) if orgs else Counter()
            cat_counts = Counter(categories) if categories else Counter()
            
            results['cluster_summaries'][cluster_id] = {
                'document_count': len(cluster_docs),
                'keywords_tfidf': cluster_keywords_tfidf,
                'keywords_frequency': cluster_keywords_freq,
                'top_organizations': dict(org_counts.most_common(5)),
                'top_categories': dict(cat_counts.most_common(5)),
                'avg_document_length': np.mean([doc['character_count'] for doc in cluster_docs])
            }
        
        # Store results
        self.clusters[method] = results
        
        logging.info(f"Document analysis complete using {method}")
        logging.info(f"Found {len(results['clusters'])} clusters")
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str = "output/grouped_results.csv") -> str:
        """
        Save analysis results to CSV file.
        
        Args:
            results: Analysis results from analyze_documents()
            output_path: Output CSV file path
            
        Returns:
            Path to saved file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Prepare data for CSV
        csv_data = []
        
        for doc in results['documents']:
            # Get cluster info
            cluster_id = doc['cluster_label']
            cluster_summary = results['cluster_summaries'].get(cluster_id, {})
            
            # Handle cluster terms based on method
            cluster_terms = []
            if results['method'] == 'bertopic':
                topic_words = results['metadata'].get('topic_words', {})
                cluster_terms = topic_words.get(cluster_id, [])
            else:
                cluster_terms_dict = results['metadata'].get('cluster_terms', {}) or results['metadata'].get('topic_words', {})
                cluster_terms = cluster_terms_dict.get(cluster_id, [])
            
            row = {
                'filename': doc['filename'],
                'document_id': doc['document_id'],
                'organization': doc['organization'],
                'category': doc['category'],
                'source_url': doc['source_url'],
                'cluster_id': cluster_id,
                'cluster_size': cluster_summary.get('document_count', 0),
                'cluster_keywords': ', '.join(cluster_terms[:10]),
                'document_keywords_tfidf': ', '.join(doc['keywords_tfidf'][:5]),
                'document_keywords_frequency': ', '.join(doc['keywords_frequency'][:5]),
                'character_count': doc['character_count'],
                'word_count': doc['word_count'],
                'summary': doc['summary'],
                'clustering_method': results['method']
            }
            
            csv_data.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        logging.info(f"Results saved to {output_path}")
        
        # Also save detailed results as JSON
        json_path = output_path.replace('.csv', '_detailed.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            # Convert numpy types for JSON serialization
            json_results = self._convert_for_json(results)
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Detailed results saved to {json_path}")
        
        return output_path
    
    def _convert_for_json(self, obj):
        """Convert numpy types and other non-serializable objects for JSON."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {str(key): self._convert_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_for_json(item) for item in obj]
        elif isinstance(obj, defaultdict):
            return {str(key): self._convert_for_json(value) for key, value in dict(obj).items()}
        else:
            return obj
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """
        Print a summary of clustering results.
        
        Args:
            results: Analysis results from analyze_documents()
        """
        print(f"\n{'='*60}")
        print(f"Document Clustering Results - {results['method'].upper()}")
        print(f"{'='*60}")
        
        print(f"Total documents: {len(results['documents'])}")
        print(f"Number of clusters: {len(results['clusters'])}")
        
        # Method-specific metrics
        metadata = results['metadata']
        if metadata.get('silhouette_score'):
            print(f"Silhouette score: {metadata['silhouette_score']:.3f}")
        if metadata.get('perplexity'):
            print(f"Perplexity: {metadata['perplexity']:.3f}")
        
        print(f"\nGlobal Keywords (TF-IDF): {', '.join(results['global_keywords']['tfidf'][:10])}")
        print(f"Global Keywords (Frequency): {', '.join(results['global_keywords']['frequency'][:10])}")
        
        print(f"\nCluster Breakdown:")
        print("-" * 40)
        
        for cluster_id in sorted(results['clusters'].keys()):
            cluster_docs = results['clusters'][cluster_id]
            cluster_summary = results['cluster_summaries'][cluster_id]
            
            print(f"\nCluster {cluster_id}: {len(cluster_docs)} documents")
            print(f"  Keywords: {', '.join(cluster_summary['keywords_tfidf'][:8])}")
            
            if cluster_summary['top_organizations']:
                top_org = list(cluster_summary['top_organizations'].keys())[0]
                print(f"  Top Organization: {top_org}")
            
            if cluster_summary['top_categories']:
                top_cat = list(cluster_summary['top_categories'].keys())[0]
                print(f"  Top Category: {top_cat}")
            
            print(f"  Avg. Length: {cluster_summary['avg_document_length']:.0f} chars")
            
            # Show first few document IDs
            doc_ids = [doc['document_id'] for doc in cluster_docs[:3]]
            print(f"  Sample Docs: {', '.join(doc_ids)}")


def group_documents(text_dir: str = "text", csv_path: str = "input/comment_links.csv",
                   method: str = "tfidf_kmeans", output_path: str = "output/grouped_results.csv",
                   **kwargs) -> str:
    """
    Main function to group documents.
    
    Args:
        text_dir: Directory containing text files
        csv_path: Path to original CSV file
        method: Clustering method
        output_path: Output CSV file path
        **kwargs: Additional parameters for clustering
        
    Returns:
        Path to output file
    """
    grouper = DocumentGrouper(text_dir, csv_path)
    
    # Load documents
    n_docs = grouper.load_documents()
    if n_docs == 0:
        raise ValueError(f"No documents found in {text_dir}")
    
    # Analyze documents
    results = grouper.analyze_documents(method, **kwargs)
    
    # Print summary
    grouper.print_summary(results)
    
    # Save results
    output_file = grouper.save_results(results, output_path)
    
    return output_file


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description="Group and cluster documents by topics and keywords")
    
    parser.add_argument('--text-dir', default='text',
                       help='Directory containing extracted text files (default: text)')
    parser.add_argument('--csv-path', default='input/comment_links.csv',
                       help='Path to original CSV file (default: input/comment_links.csv)')
    parser.add_argument('--method', default='tfidf_kmeans',
                       choices=['tfidf_kmeans', 'bertopic', 'lda'],
                       help='Clustering method (default: tfidf_kmeans)')
    parser.add_argument('--output', default='output/grouped_results.csv',
                       help='Output CSV file path (default: output/grouped_results.csv)')
    parser.add_argument('--clusters', type=int,
                       help='Number of clusters (auto-detected if not specified)')
    parser.add_argument('--min-topic-size', type=int, default=2,
                       help='Minimum topic size for BERTopic (default: 2)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging('logs')
    
    try:
        # Prepare clustering parameters
        kwargs = {}
        if args.clusters:
            if args.method in ['tfidf_kmeans']:
                kwargs['n_clusters'] = args.clusters
            elif args.method == 'lda':
                kwargs['n_topics'] = args.clusters
        
        if args.method == 'bertopic':
            kwargs['min_topic_size'] = args.min_topic_size
        
        # Group documents
        output_file = group_documents(
            text_dir=args.text_dir,
            csv_path=args.csv_path,
            method=args.method,
            output_path=args.output,
            **kwargs
        )
        
        print(f"\nGrouping complete! Results saved to:")
        print(f"  CSV: {output_file}")
        print(f"  JSON: {output_file.replace('.csv', '_detailed.json')}")
        
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise


if __name__ == "__main__":
    main()