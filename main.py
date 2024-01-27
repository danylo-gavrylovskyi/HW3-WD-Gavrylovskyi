import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

from helpers.formdataParser import parse_formdata_request
from helpers.getMetadata import get_metadata_from_file
from helpers.urlParser import parse_url

class SimpleHandler(SimpleHTTPRequestHandler):
    def _send_response(self, message, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(bytes(message, 'utf8') if content_type == 'text/html' else message)

    def do_GET(self):
        if self.path == '/':
            with open('data/docs.json', 'r') as file:
                self._send_response(json.dumps(json.load(file)))   

        splitted_path: str = self.path.split('/')
        if splitted_path[1] == 'images':
            path_to_file: str = f'public/images/{splitted_path[2]}'
            try:
                with open(path_to_file, 'rb') as file:
                    self._send_response(file.read(), content_type='image/png')
            except IOError:
                self._send_response(json.dumps({'msg': 'Error! File not found'}), status=404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.path == '/parse-url':
            try:
                url = json.loads(post_data.decode('utf-8'))['url']
                parsed_url: str = parse_url(url)
                self._send_response(json.dumps({'Info about url': parsed_url}))
            except json.JSONDecodeError:
                self._send_response('Error: Invalid JSON data received in the POST request.', status=400)

        elif self.path == '/file-info':
            formdata = parse_formdata_request(self.headers, post_data)
            metadata = get_metadata_from_file(formdata['file'], formdata['string_to_find'])
            self._send_response(json.dumps(metadata))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()