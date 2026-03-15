#!/usr/bin/env python3
"""
Pattern Miner - Core Python Analysis Engine
Handles clustering, association rules, and pattern scoring
"""

import json
import sys
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


@dataclass
class Pattern:
    """Represents a discovered pattern"""
    id: str
    type: str  # 'cluster', 'association', 'sequential', 'anomaly'
    items: List[str]
    confidence: float
    frequency: int
    importance: float
    metadata: Dict[str, Any]
    created_at: str
    source: str


@dataclass
class Insight:
    """Actionable insight derived from patterns"""
    id: str
    pattern_id: str
    title: str
    description: str
    action: str
    priority: str  # 'high', 'medium', 'low'
    expected_impact: float
    category: str


class PatternAnalyzer:
    """Core analyzer for pattern mining"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_confidence = self.config.get('min_confidence', 0.6)
        self.min_frequency = self.config.get('min_frequency', 3)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.patterns: List[Pattern] = []
        self.insights: List[Insight] = []
    
    def preprocess_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert raw data to DataFrame for analysis"""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df.get('timestamp', datetime.now()))
        return df
    
    def extract_features(self, texts: List[str]) -> np.ndarray:
        """Extract TF-IDF features from text data"""
        if not texts:
            return np.array([])
        return self.vectorizer.fit_transform(texts).toarray()
    
    def cluster_patterns(self, data: List[Dict[str, Any]], n_clusters: int = 5) -> List[Pattern]:
        """Discover clusters in data using KMeans"""
        if len(data) < n_clusters:
            return []
        
        texts = [item.get('content', str(item)) for item in data]
        features = self.extract_features(texts)
        
        if features.size == 0:
            return []
        
        kmeans = KMeans(n_clusters=min(n_clusters, len(data)), random_state=42)
        labels = kmeans.fit_predict(features)
        
        patterns = []
        for cluster_id in range(kmeans.n_clusters):
            cluster_items = [data[i] for i, label in enumerate(labels) if label == cluster_id]
            if len(cluster_items) >= self.min_frequency:
                pattern = Pattern(
                    id=f"cluster_{cluster_id}_{datetime.now().timestamp()}",
                    type='cluster',
                    items=[str(item) for item in cluster_items],
                    confidence=float(np.mean([cosine_similarity([kmeans.cluster_centers_[cluster_id]], 
                                                               [features[i]])[0][0] 
                                            for i, label in enumerate(labels) if label == cluster_id])),
                    frequency=len(cluster_items),
                    importance=self._calculate_importance(cluster_items),
                    metadata={'centroid': kmeans.cluster_centers_[cluster_id].tolist()},
                    created_at=datetime.now().isoformat(),
                    source='clustering'
                )
                patterns.append(pattern)
        
        return patterns
    
    def find_association_rules(self, data: List[Dict[str, Any]], 
                               min_support: float = 0.1) -> List[Pattern]:
        """Discover association rules between items"""
        from itertools import combinations
        from collections import Counter
        
        if len(data) < 2:
            return []
        
        # Extract item sets
        item_sets = []
        for item in data:
            if isinstance(item, dict):
                tags = item.get('tags', []) or item.get('keywords', [])
                if tags:
                    item_sets.append(set(tags))
        
        if not item_sets:
            return []
        
        # Count item frequencies
        all_items = [item for sublist in item_sets for item in sublist]
        item_counts = Counter(all_items)
        total = len(item_sets)
        
        patterns = []
        # Find frequent pairs
        pair_counts = Counter()
        for item_set in item_sets:
            for pair in combinations(item_set, 2):
                pair_counts[tuple(sorted(pair))] += 1
        
        for pair, count in pair_counts.items():
            support = count / total
            if support >= min_support:
                confidence = count / item_counts[pair[0]]
                if confidence >= self.min_confidence:
                    pattern = Pattern(
                        id=f"assoc_{pair[0]}_{pair[1]}_{datetime.now().timestamp()}",
                        type='association',
                        items=list(pair),
                        confidence=confidence,
                        frequency=count,
                        importance=support * confidence,
                        metadata={'support': support, 'antecedent': pair[0], 'consequent': pair[1]},
                        created_at=datetime.now().isoformat(),
                        source='association_rules'
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def detect_anomalies(self, data: List[Dict[str, Any]], 
                         contamination: float = 0.1) -> List[Pattern]:
        """Detect anomalous patterns in data"""
        if len(data) < 10:
            return []
        
        texts = [item.get('content', str(item)) for item in data]
        features = self.extract_features(texts)
        
        if features.size == 0:
            return []
        
        from sklearn.neighbors import LocalOutlierFactor
        lof = LocalOutlierFactor(contamination=contamination, novelty=True)
        lof.fit(features)
        predictions = lof.predict(features)
        
        patterns = []
        anomaly_indices = [i for i, pred in enumerate(predictions) if pred == -1]
        
        if anomaly_indices:
            pattern = Pattern(
                id=f"anomaly_{datetime.now().timestamp()}",
                type='anomaly',
                items=[str(data[i]) for i in anomaly_indices],
                confidence=1.0 - contamination,
                frequency=len(anomaly_indices),
                importance=0.8,  # Anomalies are often important
                metadata={'indices': anomaly_indices, 'method': 'LOF'},
                created_at=datetime.now().isoformat(),
                source='anomaly_detection'
            )
            patterns.append(pattern)
        
        return patterns
    
    def _calculate_importance(self, items: List[Dict[str, Any]]) -> float:
        """Calculate importance score based on item metadata"""
        if not items:
            return 0.0
        
        scores = []
        for item in items:
            score = 0.5  # base score
            if isinstance(item, dict):
                if item.get('priority') == 'high':
                    score += 0.3
                elif item.get('priority') == 'medium':
                    score += 0.15
                if item.get('resolved'):
                    score -= 0.1
            scores.append(score)
        
        return float(np.mean(scores))
    
    def score_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Score and rank patterns by importance"""
        for pattern in patterns:
            # Composite scoring formula
            pattern.importance = (
                0.4 * pattern.confidence +
                0.3 * min(pattern.frequency / 10, 1.0) +
                0.3 * pattern.importance
            )
        
        return sorted(patterns, key=lambda p: p.importance, reverse=True)
    
    def generate_insights(self, patterns: List[Pattern]) -> List[Insight]:
        """Generate actionable insights from patterns"""
        insights = []
        
        for pattern in patterns:
            if pattern.importance < 0.5:
                continue
            
            if pattern.type == 'cluster':
                insight = Insight(
                    id=f"insight_{pattern.id}",
                    pattern_id=pattern.id,
                    title=f"Recurring Pattern: {pattern.items[0][:50]}...",
                    description=f"Found {pattern.frequency} similar items forming a pattern",
                    action="Review and standardize this pattern",
                    priority='high' if pattern.importance > 0.8 else 'medium',
                    expected_impact=pattern.importance * 0.9,
                    category='optimization'
                )
            elif pattern.type == 'association':
                insight = Insight(
                    id=f"insight_{pattern.id}",
                    pattern_id=pattern.id,
                    title=f"Association: {pattern.items[0]} → {pattern.items[1]}",
                    description=f"These items frequently occur together (confidence: {pattern.confidence:.2f})",
                    action="Consider linking or automating these related items",
                    priority='medium',
                    expected_impact=pattern.confidence * 0.7,
                    category='automation'
                )
            elif pattern.type == 'anomaly':
                insight = Insight(
                    id=f"insight_{pattern.id}",
                    pattern_id=pattern.id,
                    title=f"Anomaly Detected: {len(pattern.items)} unusual items",
                    description="These items deviate significantly from normal patterns",
                    action="Investigate these anomalies for potential issues",
                    priority='high',
                    expected_impact=0.85,
                    category='risk'
                )
            else:
                continue
            
            insights.append(insight)
        
        return sorted(insights, key=lambda i: i.expected_impact, reverse=True)
    
    def analyze(self, data: List[Dict[str, Any]], 
                analysis_types: List[str] = None) -> Dict[str, Any]:
        """Run full analysis pipeline"""
        analysis_types = analysis_types or ['cluster', 'association', 'anomaly']
        
        all_patterns = []
        
        if 'cluster' in analysis_types:
            all_patterns.extend(self.cluster_patterns(data))
        
        if 'association' in analysis_types:
            all_patterns.extend(self.find_association_rules(data))
        
        if 'anomaly' in analysis_types:
            all_patterns.extend(self.detect_anomalies(data))
        
        # Score and rank
        scored_patterns = self.score_patterns(all_patterns)
        
        # Generate insights
        insights = self.generate_insights(scored_patterns)
        
        return {
            'patterns': [asdict(p) for p in scored_patterns],
            'insights': [asdict(i) for i in insights],
            'summary': {
                'total_patterns': len(scored_patterns),
                'total_insights': len(insights),
                'by_type': {
                    'cluster': len([p for p in scored_patterns if p.type == 'cluster']),
                    'association': len([p for p in scored_patterns if p.type == 'association']),
                    'anomaly': len([p for p in scored_patterns if p.type == 'anomaly'])
                }
            }
        }


def main():
    """CLI entry point for Python analyzer"""
    if len(sys.argv) < 2:
        print("Usage: python pattern_analyzer.py <input_json_file> [output_json_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    analyzer = PatternAnalyzer()
    results = analyzer.analyze(data)
    
    output_json = json.dumps(results, indent=2)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_json)
        print(f"Results written to {output_file}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
