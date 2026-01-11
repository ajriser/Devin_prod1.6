import os
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json


class ReportTool:
    """Tool for generating downloadable reports in various formats."""
    
    name = "report_generator"
    description = "Generate downloadable reports in PDF, Excel, and CSV formats"
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.current_data: Optional[pd.DataFrame] = None
        self.report_content: Dict[str, Any] = {}
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Load data for report generation."""
        try:
            self.current_data = data
            return {
                'success': True,
                'message': f"Loaded data with {len(data)} rows and {len(data.columns)} columns"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_content(self, section: str, content: Any) -> Dict[str, Any]:
        """Add content to the report."""
        self.report_content[section] = content
        return {
            'success': True,
            'message': f"Added content to section: {section}"
        }
    
    def generate_pdf_report(self, title: str = "Data Analysis Report",
                            include_data: bool = True,
                            include_stats: bool = True,
                            charts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a PDF report."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='CustomTitle',
                                      parent=styles['Heading1'],
                                      fontSize=24,
                                      spaceAfter=30,
                                      alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='SectionHeader',
                                      parent=styles['Heading2'],
                                      fontSize=16,
                                      spaceAfter=12,
                                      spaceBefore=20))
            styles.add(ParagraphStyle(name='BodyText',
                                      parent=styles['Normal'],
                                      fontSize=10,
                                      spaceAfter=12))
            
            story = []
            
            story.append(Paragraph(title, styles['CustomTitle']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                   styles['BodyText']))
            story.append(Spacer(1, 20))
            
            if self.current_data is not None:
                story.append(Paragraph("Dataset Overview", styles['SectionHeader']))
                overview_text = f"""
                Total Rows: {len(self.current_data)}<br/>
                Total Columns: {len(self.current_data.columns)}<br/>
                Columns: {', '.join(self.current_data.columns.tolist())}
                """
                story.append(Paragraph(overview_text, styles['BodyText']))
                story.append(Spacer(1, 12))
            
            if include_stats and self.current_data is not None:
                story.append(Paragraph("Statistical Summary", styles['SectionHeader']))
                
                numeric_df = self.current_data.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    stats_df = numeric_df.describe().round(2)
                    
                    table_data = [['Statistic'] + stats_df.columns.tolist()]
                    for idx in stats_df.index:
                        row = [idx] + [str(v) for v in stats_df.loc[idx].values]
                        table_data.append(row)
                    
                    col_widths = [80] + [60] * len(stats_df.columns)
                    if sum(col_widths) > 450:
                        col_widths = [80] + [min(60, 370 // len(stats_df.columns))] * len(stats_df.columns)
                    
                    table = Table(table_data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 20))
            
            for section, content in self.report_content.items():
                story.append(Paragraph(section, styles['SectionHeader']))
                if isinstance(content, str):
                    for para in content.split('\n\n'):
                        if para.strip():
                            story.append(Paragraph(para.replace('\n', '<br/>'), styles['BodyText']))
                elif isinstance(content, dict):
                    content_text = json.dumps(content, indent=2)
                    story.append(Paragraph(f"<pre>{content_text}</pre>", styles['BodyText']))
                story.append(Spacer(1, 12))
            
            if charts:
                story.append(PageBreak())
                story.append(Paragraph("Charts and Visualizations", styles['SectionHeader']))
                for chart_path in charts:
                    if os.path.exists(chart_path) and chart_path.endswith(('.png', '.jpg', '.jpeg')):
                        img = Image(chart_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 20))
            
            if include_data and self.current_data is not None:
                story.append(PageBreak())
                story.append(Paragraph("Data Sample (First 20 Rows)", styles['SectionHeader']))
                
                sample_df = self.current_data.head(20)
                table_data = [sample_df.columns.tolist()]
                for _, row in sample_df.iterrows():
                    table_data.append([str(v)[:20] for v in row.values])
                
                n_cols = len(sample_df.columns)
                col_width = min(60, 450 // n_cols)
                
                table = Table(table_data, colWidths=[col_width] * n_cols)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            
            doc.build(story)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f"PDF report generated: {filename}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_excel_report(self, title: str = "Data Analysis Report",
                              include_stats: bool = True,
                              include_charts: bool = False) -> Dict[str, Any]:
        """Generate an Excel report with multiple sheets."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                self.current_data.to_excel(writer, sheet_name='Data', index=False)
                
                if include_stats:
                    numeric_df = self.current_data.select_dtypes(include=['number'])
                    if not numeric_df.empty:
                        stats_df = numeric_df.describe()
                        stats_df.to_excel(writer, sheet_name='Statistics')
                    
                    info_data = {
                        'Metric': ['Total Rows', 'Total Columns', 'Memory Usage (MB)'],
                        'Value': [
                            len(self.current_data),
                            len(self.current_data.columns),
                            round(self.current_data.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                        ]
                    }
                    info_df = pd.DataFrame(info_data)
                    info_df.to_excel(writer, sheet_name='Overview', index=False)
                
                for section, content in self.report_content.items():
                    if isinstance(content, pd.DataFrame):
                        sheet_name = section[:31]
                        content.to_excel(writer, sheet_name=sheet_name, index=False)
                    elif isinstance(content, dict):
                        content_df = pd.DataFrame([content])
                        sheet_name = section[:31]
                        content_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f"Excel report generated: {filename}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_csv_export(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Export data to CSV format."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            self.current_data.to_csv(filepath, index=False)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'rows': len(self.current_data),
                'message': f"CSV export generated: {filename}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_json_export(self, filename: Optional[str] = None,
                             orient: str = 'records') -> Dict[str, Any]:
        """Export data to JSON format."""
        if self.current_data is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_export_{timestamp}.json"
            
            filepath = os.path.join(self.output_dir, filename)
            self.current_data.to_json(filepath, orient=orient, indent=2)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'rows': len(self.current_data),
                'message': f"JSON export generated: {filename}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_summary_report(self, summary_text: str, 
                                insights: Optional[str] = None) -> Dict[str, Any]:
        """Generate a text-based summary report."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("DATA ANALYSIS SUMMARY REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                if self.current_data is not None:
                    f.write("DATASET OVERVIEW\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Rows: {len(self.current_data)}\n")
                    f.write(f"Columns: {len(self.current_data.columns)}\n")
                    f.write(f"Columns: {', '.join(self.current_data.columns.tolist())}\n\n")
                
                f.write("SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(summary_text + "\n\n")
                
                if insights:
                    f.write("KEY INSIGHTS\n")
                    f.write("-" * 40 + "\n")
                    f.write(insights + "\n\n")
                
                for section, content in self.report_content.items():
                    f.write(f"\n{section.upper()}\n")
                    f.write("-" * 40 + "\n")
                    if isinstance(content, str):
                        f.write(content + "\n")
                    else:
                        f.write(str(content) + "\n")
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f"Summary report generated: {filename}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_content(self) -> Dict[str, Any]:
        """Clear all report content."""
        self.report_content.clear()
        return {
            'success': True,
            'message': "Report content cleared"
        }
    
    def list_reports(self) -> Dict[str, Any]:
        """List all generated reports."""
        try:
            reports = []
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    reports.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'message': f"Found {len(reports)} reports"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for the tool."""
        actions = {
            'load': lambda: self.load_data(kwargs.get('data')),
            'add_content': lambda: self.add_content(kwargs.get('section', ''), kwargs.get('content')),
            'pdf': lambda: self.generate_pdf_report(
                kwargs.get('title', 'Data Analysis Report'),
                kwargs.get('include_data', True),
                kwargs.get('include_stats', True),
                kwargs.get('charts')
            ),
            'excel': lambda: self.generate_excel_report(
                kwargs.get('title', 'Data Analysis Report'),
                kwargs.get('include_stats', True),
                kwargs.get('include_charts', False)
            ),
            'csv': lambda: self.generate_csv_export(kwargs.get('filename')),
            'json': lambda: self.generate_json_export(kwargs.get('filename'), kwargs.get('orient', 'records')),
            'summary': lambda: self.generate_summary_report(
                kwargs.get('summary_text', ''),
                kwargs.get('insights')
            ),
            'clear': self.clear_content,
            'list': self.list_reports
        }
        
        if action not in actions:
            return {'success': False, 'error': f'Unknown action: {action}'}
        
        return actions[action]() if callable(actions[action]) else actions[action]
