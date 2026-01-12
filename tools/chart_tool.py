import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
from typing import Dict, Any, Optional, List
import base64
from io import BytesIO


class ChartTool:
    """Tool for generating various charts and visualizations."""
    
    name = "chart_generator"
    description = "Generate charts and visualizations including bar charts, line charts, scatter plots, histograms, heatmaps, and more"
    
    def __init__(self, output_dir: str = "static/charts"):
        self.output_dir = output_dir
        self.current_data: Optional[pd.DataFrame] = None
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('seaborn-v0_8-whitegrid')
        self.color_palette = px.colors.qualitative.Set2
    
    def load_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Load data for visualization."""
        try:
            self.current_data = data
            return {
                'success': True,
                'message': f"Loaded data with {len(data)} rows and {len(data.columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save_matplotlib_chart(self, fig, filename: str) -> str:
        """Save matplotlib figure and return path."""
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return filepath
    
    def _save_plotly_chart(self, fig, filename: str) -> str:
        """Save plotly figure as HTML and image."""
        html_path = os.path.join(self.output_dir, filename.replace('.png', '.html'))
        img_path = os.path.join(self.output_dir, filename)
        
        fig.write_html(html_path)
        try:
            fig.write_image(img_path)
        except Exception:
            pass
        
        return html_path
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return img_str
    
    def bar_chart(self, x: str, y: str, title: str = "Bar Chart", 
                  color: Optional[str] = None, orientation: str = 'v') -> Dict[str, Any]:
        """Create a bar chart."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.bar(
                df, x=x, y=y, color=color,
                title=title,
                orientation=orientation,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"bar_chart_{x}_{y}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'bar',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Bar chart created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def line_chart(self, x: str, y: str, title: str = "Line Chart",
                   color: Optional[str] = None) -> Dict[str, Any]:
        """Create a line chart."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.line(
                df, x=x, y=y, color=color,
                title=title,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"line_chart_{x}_{y}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'line',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Line chart created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scatter_plot(self, x: str, y: str, title: str = "Scatter Plot",
                     color: Optional[str] = None, size: Optional[str] = None) -> Dict[str, Any]:
        """Create a scatter plot."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.scatter(
                df, x=x, y=y, color=color, size=size,
                title=title,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"scatter_{x}_{y}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'scatter',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Scatter plot created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def histogram(self, column: str, title: str = "Histogram",
                  bins: int = 30, color: Optional[str] = None) -> Dict[str, Any]:
        """Create a histogram."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.histogram(
                df, x=column, color=color,
                title=title,
                nbins=bins,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"histogram_{column}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'histogram',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Histogram created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def box_plot(self, y: str, x: Optional[str] = None, 
                 title: str = "Box Plot") -> Dict[str, Any]:
        """Create a box plot."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.box(
                df, x=x, y=y,
                title=title,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"boxplot_{y}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'box',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Box plot created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def heatmap(self, title: str = "Correlation Heatmap") -> Dict[str, Any]:
        """Create a correlation heatmap."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {'success': False, 'error': 'No numeric columns for heatmap'}
            
            corr_matrix = numeric_df.corr()
            
            fig = px.imshow(
                corr_matrix,
                title=title,
                color_continuous_scale='RdBu_r',
                aspect='auto',
                text_auto='.2f'
            )
            fig.update_layout(template='plotly_white')
            
            filename = "correlation_heatmap.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'heatmap',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Heatmap created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pie_chart(self, values: str, names: str, 
                  title: str = "Pie Chart") -> Dict[str, Any]:
        """Create a pie chart."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            fig = px.pie(
                df, values=values, names=names,
                title=title,
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = f"pie_chart_{names}.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'pie',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Pie chart created: {title}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def distribution_plot(self, columns: List[str], 
                          title: str = "Distribution Plot") -> Dict[str, Any]:
        """Create distribution plots for multiple columns."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            n_cols = len(columns)
            
            fig = make_subplots(rows=1, cols=n_cols, subplot_titles=columns)
            
            for i, col in enumerate(columns, 1):
                fig.add_trace(
                    go.Histogram(x=df[col], name=col, marker_color=self.color_palette[i % len(self.color_palette)]),
                    row=1, col=i
                )
            
            fig.update_layout(title_text=title, template='plotly_white', showlegend=False)
            
            filename = "distribution_plot.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'distribution',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Distribution plot created for {len(columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pair_plot(self, columns: Optional[List[str]] = None, 
                  color: Optional[str] = None) -> Dict[str, Any]:
        """Create a pair plot (scatter matrix)."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            df = self.current_data
            
            if columns:
                plot_df = df[columns]
            else:
                plot_df = df.select_dtypes(include=[np.number])
            
            if len(plot_df.columns) > 6:
                plot_df = plot_df.iloc[:, :6]
            
            fig = px.scatter_matrix(
                df,
                dimensions=plot_df.columns.tolist(),
                color=color,
                title="Pair Plot",
                color_discrete_sequence=self.color_palette
            )
            fig.update_layout(template='plotly_white')
            
            filename = "pair_plot.html"
            filepath = self._save_plotly_chart(fig, filename)
            
            return {
                'success': True,
                'chart_type': 'pair_plot',
                'filepath': filepath,
                'chart_json': fig.to_json(),
                'message': f"Pair plot created for {len(plot_df.columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def custom_chart(self, chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom chart based on configuration."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            chart_type = chart_config.get('type', 'bar')
            
            chart_methods = {
                'bar': self.bar_chart,
                'line': self.line_chart,
                'scatter': self.scatter_plot,
                'histogram': self.histogram,
                'box': self.box_plot,
                'heatmap': self.heatmap,
                'pie': self.pie_chart
            }
            
            if chart_type not in chart_methods:
                return {'success': False, 'error': f'Unknown chart type: {chart_type}'}
            
            params = {k: v for k, v in chart_config.items() if k != 'type'}
            return chart_methods[chart_type](**params)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'load': lambda: self.load_data(kwargs.get('data')),
            'bar': lambda: self.bar_chart(
                kwargs.get('x', ''), kwargs.get('y', ''),
                kwargs.get('title', 'Bar Chart'), kwargs.get('color'),
                kwargs.get('orientation', 'v')
            ),
            'line': lambda: self.line_chart(
                kwargs.get('x', ''), kwargs.get('y', ''),
                kwargs.get('title', 'Line Chart'), kwargs.get('color')
            ),
            'scatter': lambda: self.scatter_plot(
                kwargs.get('x', ''), kwargs.get('y', ''),
                kwargs.get('title', 'Scatter Plot'), kwargs.get('color'), kwargs.get('size')
            ),
            'histogram': lambda: self.histogram(
                kwargs.get('column', ''), kwargs.get('title', 'Histogram'),
                kwargs.get('bins', 30), kwargs.get('color')
            ),
            'box': lambda: self.box_plot(
                kwargs.get('y', ''), kwargs.get('x'),
                kwargs.get('title', 'Box Plot')
            ),
            'heatmap': lambda: self.heatmap(kwargs.get('title', 'Correlation Heatmap')),
            'pie': lambda: self.pie_chart(
                kwargs.get('values', ''), kwargs.get('names', ''),
                kwargs.get('title', 'Pie Chart')
            ),
            'distribution': lambda: self.distribution_plot(
                kwargs.get('columns', []), kwargs.get('title', 'Distribution Plot')
            ),
            'pair_plot': lambda: self.pair_plot(kwargs.get('columns'), kwargs.get('color')),
            'custom': lambda: self.custom_chart(kwargs.get('config', {}))
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
