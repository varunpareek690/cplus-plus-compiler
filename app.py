import os
import base64
import subprocess
import json
import tempfile

def lambda_handler(event, context):
    try:
       
        os.environ['PATH'] += ':/usr/bin' 

        with tempfile.TemporaryDirectory() as temp_dir:
            code = base64.b64decode(event['body']['code']).decode('utf-8')
            file_path = os.path.join(temp_dir, 'main.cpp')
            
            with open(file_path, 'w') as cpp_file:
                cpp_file.write(code)
            
            compile_process = subprocess.run(
                ['g++', '-o', os.path.join(temp_dir, 'main'), file_path],
                capture_output=True, text=True
            )
            
            if compile_process.returncode != 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'status-code': 400,
                        'message': 'Compilation failed',
                        'output': base64.b64encode(compile_process.stderr.encode('utf-8')).decode('utf-8')
                    })
                }
            
            concatenated_inputs = '\n'.join(
                [base64.b64decode(input_value).decode('utf-8') for input_value in event['body'].get('input', [])]
            )
            
            run_process = subprocess.Popen(
                [os.path.join(temp_dir, 'main')],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            run_stdout, run_stderr = run_process.communicate(input=concatenated_inputs)
            
            if run_process.returncode != 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'status-code': 400,
                        'message': 'Execution failed',
                        'output': base64.b64encode(run_stderr.encode('utf-8')).decode('utf-8'),
                        'input': base64.b64encode(concatenated_inputs.encode('utf-8')).decode('utf-8')
                    })
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status-code': 200,
                    'message': 'success',
                    'output': base64.b64encode(run_stdout.encode('utf-8')).decode('utf-8'),
                    'input': base64.b64encode(concatenated_inputs.encode('utf-8')).decode('utf-8')
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status-code': 500,
                'message': 'Internal server error',
                'output': base64.b64encode(str(e).encode('utf-8')).decode('utf-8')
            })
        }
