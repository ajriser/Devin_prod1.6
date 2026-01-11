import os
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import json

from tools import (
    SnowflakeTool, SQLServerTool, PDFLoaderTool,
    EDATool, ChartTool, ReportTool
)

main_bp = Blueprint('main', __name__)

snowflake_tool = SnowflakeTool()
sqlserver_tool = SQLServerTool()
pdf_tool = PDFLoaderTool(upload_dir='uploads')
eda_tool = EDATool()
chart_tool = ChartTool(output_dir='static/charts')
report_tool = ReportTool(output_dir='reports')

current_dataframe = None


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/api/snowflake/connect', methods=['POST'])
def snowflake_connect():
    data = request.json
    config = {
        'account': data.get('account', ''),
        'user': data.get('user', ''),
        'password': data.get('password', ''),
        'warehouse': data.get('warehouse', ''),
        'database': data.get('database', ''),
        'schema': data.get('schema', '')
    }
    result = snowflake_tool.connect(config)
    return jsonify(result)


@main_bp.route('/api/snowflake/query', methods=['POST'])
def snowflake_query():
    global current_dataframe
    data = request.json
    query = data.get('query', '')
    result = snowflake_tool.execute_query(query)
    
    if result['success'] and 'data' in result:
        current_dataframe = result['data']
        eda_tool.load_data(current_dataframe)
        chart_tool.load_data(current_dataframe)
        report_tool.load_data(current_dataframe)
        
        result['data'] = result['data'].head(100).to_dict('records')
        result['columns'] = list(current_dataframe.columns)
    
    return jsonify(result)


@main_bp.route('/api/snowflake/tables', methods=['GET'])
def snowflake_tables():
    result = snowflake_tool.get_tables()
    if result['success'] and 'data' in result:
        result['data'] = result['data'].to_dict('records')
    return jsonify(result)


@main_bp.route('/api/sqlserver/connect', methods=['POST'])
def sqlserver_connect():
    data = request.json
    config = {
        'host': data.get('host', ''),
        'port': data.get('port', '1433'),
        'database': data.get('database', ''),
        'user': data.get('user', ''),
        'password': data.get('password', '')
    }
    result = sqlserver_tool.connect(config)
    return jsonify(result)


@main_bp.route('/api/sqlserver/query', methods=['POST'])
def sqlserver_query():
    global current_dataframe
    data = request.json
    query = data.get('query', '')
    result = sqlserver_tool.execute_query(query)
    
    if result['success'] and 'data' in result:
        current_dataframe = result['data']
        eda_tool.load_data(current_dataframe)
        chart_tool.load_data(current_dataframe)
        report_tool.load_data(current_dataframe)
        
        result['data'] = result['data'].head(100).to_dict('records')
        result['columns'] = list(current_dataframe.columns)
    
    return jsonify(result)


@main_bp.route('/api/sqlserver/tables', methods=['GET'])
def sqlserver_tables():
    result = sqlserver_tool.get_tables()
    if result['success'] and 'data' in result:
        result['data'] = result['data'].to_dict('records')
    return jsonify(result)


@main_bp.route('/api/pdf/upload', methods=['POST'])
def pdf_upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename, {'pdf'}):
        return jsonify({'success': False, 'error': 'Only PDF files are allowed'})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    result = pdf_tool.load_pdf(filepath)
    return jsonify(result)


@main_bp.route('/api/pdf/list', methods=['GET'])
def pdf_list():
    result = pdf_tool.get_loaded_documents()
    return jsonify(result)


@main_bp.route('/api/pdf/context', methods=['GET'])
def pdf_context():
    filenames = request.args.getlist('files')
    result = pdf_tool.get_combined_context(filenames if filenames else None)
    return jsonify(result)


@main_bp.route('/api/pdf/clear', methods=['POST'])
def pdf_clear():
    result = pdf_tool.clear_documents()
    return jsonify(result)


@main_bp.route('/api/data/upload', methods=['POST'])
def data_upload():
    global current_dataframe
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename, {'csv', 'xlsx', 'xls', 'json'}):
        return jsonify({'success': False, 'error': 'Only CSV, Excel, and JSON files are allowed'})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    try:
        if filename.endswith('.csv'):
            current_dataframe = pd.read_csv(filepath)
        elif filename.endswith(('.xlsx', '.xls')):
            current_dataframe = pd.read_excel(filepath)
        elif filename.endswith('.json'):
            current_dataframe = pd.read_json(filepath)
        
        eda_tool.load_data(current_dataframe)
        chart_tool.load_data(current_dataframe)
        report_tool.load_data(current_dataframe)
        
        return jsonify({
            'success': True,
            'rows': len(current_dataframe),
            'columns': list(current_dataframe.columns),
            'data': current_dataframe.head(100).to_dict('records'),
            'message': f'Loaded {filename} with {len(current_dataframe)} rows'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@main_bp.route('/api/eda/info', methods=['GET'])
def eda_info():
    result = eda_tool.get_basic_info()
    return jsonify(result)


@main_bp.route('/api/eda/statistics', methods=['GET'])
def eda_statistics():
    columns = request.args.getlist('columns')
    result = eda_tool.get_statistics(columns if columns else None)
    return jsonify(result)


@main_bp.route('/api/eda/correlations', methods=['GET'])
def eda_correlations():
    method = request.args.get('method', 'pearson')
    result = eda_tool.get_correlations(method)
    return jsonify(result)


@main_bp.route('/api/eda/value_counts', methods=['GET'])
def eda_value_counts():
    column = request.args.get('column', '')
    top_n = int(request.args.get('top_n', 10))
    result = eda_tool.get_value_counts(column, top_n)
    return jsonify(result)


@main_bp.route('/api/eda/outliers', methods=['GET'])
def eda_outliers():
    column = request.args.get('column', '')
    method = request.args.get('method', 'iqr')
    result = eda_tool.detect_outliers(column, method)
    return jsonify(result)


@main_bp.route('/api/eda/quality', methods=['GET'])
def eda_quality():
    result = eda_tool.get_data_quality_report()
    return jsonify(result)


@main_bp.route('/api/eda/full_report', methods=['GET'])
def eda_full_report():
    result = eda_tool.get_full_eda_report()
    return jsonify(result)


@main_bp.route('/api/chart/create', methods=['POST'])
def chart_create():
    data = request.json
    chart_type = data.get('type', 'bar')
    
    chart_methods = {
        'bar': lambda: chart_tool.bar_chart(
            data.get('x'), data.get('y'),
            data.get('title', 'Bar Chart'),
            data.get('color'), data.get('orientation', 'v')
        ),
        'line': lambda: chart_tool.line_chart(
            data.get('x'), data.get('y'),
            data.get('title', 'Line Chart'),
            data.get('color')
        ),
        'scatter': lambda: chart_tool.scatter_plot(
            data.get('x'), data.get('y'),
            data.get('title', 'Scatter Plot'),
            data.get('color'), data.get('size')
        ),
        'histogram': lambda: chart_tool.histogram(
            data.get('column'),
            data.get('title', 'Histogram'),
            data.get('bins', 30),
            data.get('color')
        ),
        'box': lambda: chart_tool.box_plot(
            data.get('y'), data.get('x'),
            data.get('title', 'Box Plot')
        ),
        'heatmap': lambda: chart_tool.heatmap(data.get('title', 'Correlation Heatmap')),
        'pie': lambda: chart_tool.pie_chart(
            data.get('values'), data.get('names'),
            data.get('title', 'Pie Chart')
        ),
        'distribution': lambda: chart_tool.distribution_plot(
            data.get('columns', []),
            data.get('title', 'Distribution Plot')
        ),
        'pair_plot': lambda: chart_tool.pair_plot(
            data.get('columns'), data.get('color')
        )
    }
    
    if chart_type not in chart_methods:
        return jsonify({'success': False, 'error': f'Unknown chart type: {chart_type}'})
    
    result = chart_methods[chart_type]()
    return jsonify(result)


@main_bp.route('/api/report/pdf', methods=['POST'])
def report_pdf():
    data = request.json
    result = report_tool.generate_pdf_report(
        title=data.get('title', 'Data Analysis Report'),
        include_data=data.get('include_data', True),
        include_stats=data.get('include_stats', True),
        charts=data.get('charts')
    )
    return jsonify(result)


@main_bp.route('/api/report/excel', methods=['POST'])
def report_excel():
    data = request.json
    result = report_tool.generate_excel_report(
        title=data.get('title', 'Data Analysis Report'),
        include_stats=data.get('include_stats', True)
    )
    return jsonify(result)


@main_bp.route('/api/report/csv', methods=['POST'])
def report_csv():
    data = request.json
    result = report_tool.generate_csv_export(data.get('filename'))
    return jsonify(result)


@main_bp.route('/api/report/json', methods=['POST'])
def report_json():
    data = request.json
    result = report_tool.generate_json_export(
        data.get('filename'),
        data.get('orient', 'records')
    )
    return jsonify(result)


@main_bp.route('/api/report/add_content', methods=['POST'])
def report_add_content():
    data = request.json
    section = data.get('section', '')
    content = data.get('content', '')
    result = report_tool.add_content(section, content)
    return jsonify(result)


@main_bp.route('/api/report/list', methods=['GET'])
def report_list():
    result = report_tool.list_reports()
    return jsonify(result)


@main_bp.route('/api/report/download/<filename>')
def report_download(filename):
    filepath = os.path.join('reports', secure_filename(filename))
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'success': False, 'error': 'File not found'}), 404


@main_bp.route('/api/data/current', methods=['GET'])
def data_current():
    global current_dataframe
    if current_dataframe is None:
        return jsonify({'success': False, 'error': 'No data loaded'})
    
    return jsonify({
        'success': True,
        'rows': len(current_dataframe),
        'columns': list(current_dataframe.columns),
        'dtypes': {col: str(dtype) for col, dtype in current_dataframe.dtypes.items()},
        'data': current_dataframe.head(100).to_dict('records')
    })
