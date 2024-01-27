from urllib import parse

def parse_url(url: str):
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