import re

def parse_formdata_request(headers, post_data):
    body_splitter = headers["Content-Type"].split("boundary=")[1]
    parsed_post_data = post_data.split(b"--" + body_splitter.encode())[1:-1]
    formdata = {}
    for data in parsed_post_data:
        names, content = data.split(b'\r\n\r\n', 1)
        content = content.rstrip(b'\r\n')
        name = names.split(b'\r\n')[1]
        parsed_name = re.findall(r'name="([^"]+)"', name.decode())[0]
        formdata[parsed_name] = content.decode('utf-8')
    return formdata