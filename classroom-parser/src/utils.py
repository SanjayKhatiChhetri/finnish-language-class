import os
from .parser import ClassroomParser
from .models import WeeklyData

def process_file(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    parser = ClassroomParser(html)
    items = parser.parse_stream_items()
    weekly_data = parser.group_by_weeks(items)
    ts_code = parser.generate_typescript(weekly_data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ts_code)

def batch_process(input_dir: str, output_dir: str):
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.ts")
            process_file(input_path, output_path)