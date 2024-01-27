import re
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib import parse

class SimpleHandler(SimpleHTTPRequestHandler):
    def _send_response(self, message, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(bytes(message, 'utf8') if content_type == 'text/html' else message)

    def parse_formdata_request(self, post_data):
        body_splitter = self.headers["Content-Type"].split("boundary=")[1]
        parsed_post_data = post_data.split(b"--" + body_splitter.encode())[1:-1]
        formdata = {}
        for data in parsed_post_data:
            names, content = data.split(b'\r\n\r\n', 1)
            content = content.rstrip(b'\r\n')
            name = names.split(b'\r\n')[1]
            parsed_name = re.findall(r'name="([^"]+)"', name.decode())[0]
            formdata[parsed_name] = content.decode('utf-8')
        return formdata
    
    def get_metadata_from_file(self, text: str, str_to_find: str):
        metadata = {}
        metadata['Length of whole text'] = len(text)
        metadata['Amount of alphanumeric symbols'] = len([symb for symb in text if symb.isalnum()])
        metadata['Number of occurrences of that string in the text'] = text.lower().count(str_to_find.lower())
        return metadata

    def parse_url(self, url: str):
        url_info: str = ''
        parsed_url = parse.urlparse(url)

        protocol: str = f'It has {parsed_url.scheme} protocol. ' if parsed_url.scheme else 'It does not have protocol. '
        url_info += protocol

        domain: str = f'Domain is {parsed_url.netloc}. ' if parsed_url.netloc else 'It does not have domain. '
        url_info += domain

        splitted_path = parsed_url.path.split('/')[1:]
        path: str = f'The path to the resource has {len(splitted_path)} steps - {" and ".join(splitted_path)}. ' if parsed_url.path else 'No path to the resource. '
        url_info += path

        params_dict = dict(parse.parse_qsl(parse.urlsplit(url).query))
        params: str = f'Query parameters ({len(params_dict)}) are present: {params_dict}' if params_dict else 'It does not have query parameters'
        url_info += params

        return url_info

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
                parsed_url: str = self.parse_url(url)
                self._send_response(json.dumps({'Info about url': parsed_url}))
            except json.JSONDecodeError:
                self._send_response('Error: Invalid JSON data received in the POST request.', status=400)

        elif self.path == '/file-info':
            formdata = self.parse_formdata_request(post_data)
            metadata = self.get_metadata_from_file(formdata['file'], formdata['string_to_find'])
            self._send_response(json.dumps(metadata))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()