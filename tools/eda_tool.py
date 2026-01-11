import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json


class EDATool:
    """Tool for performing Exploratory Data Analysis on datasets."""
    
    name = "eda_analyzer"
    description = "Perform exploratory data analysis including statistics, distributions, correlations, and data quality checks"
    
    def __init__(self):
        self.current_data: Optional[pd.DataFrame] = None
        self.analysis_results: Dict[str, Any] = {}
    
    def load_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Load data for analysis."""
        try:
            self.current_data = data
            return {
                'success': True,
                'rows': len(data),
                'columns': len(data.columns),
                'column_names': list(data.columns),
                'message': f"Loaded dataset with {len(data)} rows and {len(data.columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic information about the dataset."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            info = {
                'success': True,
                'shape': {'rows': len(df), 'columns': len(df.columns)},
                'columns': [],
                'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'duplicates': int(df.duplicated().sum())
            }
            
            for col in df.columns:
                col_info = {
                    'name': col,
                    'dtype': str(df[col].dtype),
                    'non_null': int(df[col].notna().sum()),
                    'null_count': int(df[col].isna().sum()),
                    'null_percentage': round(df[col].isna().sum() / len(df) * 100, 2),
                    'unique_values': int(df[col].nunique())
                }
                info['columns'].append(col_info)
            
            info['message'] = f"Dataset: {info['shape']['rows']} rows x {info['shape']['columns']} columns, {info['memory_usage']:.2f} MB"
            return info
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_statistics(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get descriptive statistics for numeric columns."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            if columns:
                numeric_cols = [c for c in columns if c in df.select_dtypes(include=[np.number]).columns]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'success': False, 'error': 'No numeric columns found'}
            
            stats = {}
            for col in numeric_cols:
                col_stats = {
                    'count': int(df[col].count()),
                    'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                    'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    'q25': float(df[col].quantile(0.25)) if not pd.isna(df[col].quantile(0.25)) else None,
                    'q75': float(df[col].quantile(0.75)) if not pd.isna(df[col].quantile(0.75)) else None,
                    'skewness': float(df[col].skew()) if not pd.isna(df[col].skew()) else None,
                    'kurtosis': float(df[col].kurtosis()) if not pd.isna(df[col].kurtosis()) else None
                }
                stats[col] = col_stats
            
            self.analysis_results['statistics'] = stats
            
            return {
                'success': True,
                'statistics': stats,
                'columns_analyzed': numeric_cols,
                'message': f"Computed statistics for {len(numeric_cols)} numeric columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_correlations(self, method: str = 'pearson') -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {'success': False, 'error': 'No numeric columns for correlation'}
            
            corr_matrix = numeric_df.corr(method=method)
            
            correlations = corr_matrix.to_dict()
            
            high_correlations = []
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns):
                    if i < j:
                        corr_val = corr_matrix.loc[col1, col2]
                        if abs(corr_val) > 0.7:
                            high_correlations.append({
                                'column1': col1,
                                'column2': col2,
                                'correlation': round(corr_val, 4)
                            })
            
            self.analysis_results['correlations'] = correlations
            
            return {
                'success': True,
                'correlation_matrix': correlations,
                'high_correlations': high_correlations,
                'method': method,
                'message': f"Computed {method} correlations for {len(numeric_df.columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_value_counts(self, column: str, top_n: int = 10) -> Dict[str, Any]:
        """Get value counts for a categorical column."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            if column not in self.current_data.columns:
                return {'success': False, 'error': f'Column not found: {column}'}
            
            value_counts = self.current_data[column].value_counts().head(top_n)
            
            return {
                'success': True,
                'column': column,
                'value_counts': value_counts.to_dict(),
                'total_unique': int(self.current_data[column].nunique()),
                'message': f"Top {top_n} values for {column}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_outliers(self, column: str, method: str = 'iqr') -> Dict[str, Any]:
        """Detect outliers in a numeric column."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            if column not in self.current_data.columns:
                return {'success': False, 'error': f'Column not found: {column}'}
            
            data = self.current_data[column].dropna()
            
            if method == 'iqr':
                q1 = data.quantile(0.25)
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = data[(data < lower_bound) | (data > upper_bound)]
            elif method == 'zscore':
                mean = data.mean()
                std = data.std()
                z_scores = (data - mean) / std
                outliers = data[abs(z_scores) > 3]
                lower_bound = mean - 3 * std
                upper_bound = mean + 3 * std
            else:
                return {'success': False, 'error': f'Unknown method: {method}'}
            
            return {
                'success': True,
                'column': column,
                'method': method,
                'outlier_count': len(outliers),
                'outlier_percentage': round(len(outliers) / len(data) * 100, 2),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'message': f"Found {len(outliers)} outliers ({round(len(outliers) / len(data) * 100, 2)}%) in {column}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive data quality report."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            report = {
                'success': True,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'total_cells': len(df) * len(df.columns),
                'missing_cells': int(df.isna().sum().sum()),
                'missing_percentage': round(df.isna().sum().sum() / (len(df) * len(df.columns)) * 100, 2),
                'duplicate_rows': int(df.duplicated().sum()),
                'duplicate_percentage': round(df.duplicated().sum() / len(df) * 100, 2),
                'column_quality': []
            }
            
            for col in df.columns:
                col_quality = {
                    'name': col,
                    'dtype': str(df[col].dtype),
                    'missing': int(df[col].isna().sum()),
                    'missing_pct': round(df[col].isna().sum() / len(df) * 100, 2),
                    'unique': int(df[col].nunique()),
                    'unique_pct': round(df[col].nunique() / len(df) * 100, 2)
                }
                report['column_quality'].append(col_quality)
            
            report['message'] = f"Data quality: {100 - report['missing_percentage']:.1f}% complete, {report['duplicate_percentage']:.1f}% duplicates"
            
            return report
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_full_eda_report(self) -> Dict[str, Any]:
        """Generate a complete EDA report."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            report = {
                'success': True,
                'basic_info': self.get_basic_info(),
                'statistics': self.get_statistics(),
                'correlations': self.get_correlations(),
                'data_quality': self.get_data_quality_report()
            }
            
            report['message'] = "Complete EDA report generated"
            return report
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'load': lambda: self.load_data(kwargs.get('data')),
            'info': self.get_basic_info,
            'statistics': lambda: self.get_statistics(kwargs.get('columns')),
            'correlations': lambda: self.get_correlations(kwargs.get('method', 'pearson')),
            'value_counts': lambda: self.get_value_counts(kwargs.get('column', ''), kwargs.get('top_n', 10)),
            'outliers': lambda: self.detect_outliers(kwargs.get('column', ''), kwargs.get('method', 'iqr')),
            'quality': self.get_data_quality_report,
            'full_report': self.get_full_eda_report
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
