from __future__ import absolute_import, print_function
import pkg_resources as pkr
import argparse
import logging
import re
#import json
#from jinja2 import Environment

#def render_template(jinja_env, input_file, data=None):
#    payload = {'env': os.environ(),
#               'data': data}
#    if input_file == '-':
#        return env.from_string(sys.stdin.read()).render(payload)
#    else:
#        with open(input_file, 'r') as tfd:
#            return env.from_string(tfd.read()).render(payload)

#class TemplateEngine(object):
#    __metaclass__ = ABCMeta
#
#    @abstractmethod
#    def render(self, data):
#        pass
#
#class Jinja2Engine(TemplateEngine):
#
#    def __init__(self):
#        pass
#
#    def render
#
#class DataSource(object):
#    __metaclass__ = ABCMeta

#def build_environment(args):
#    extensions = ['jinja2.ext.do',
#                  'jinja2.ext.loopcontrols',
#                  'jinja2.ext.with_',
#                  'jinja2.ext.autoescape']
#    env = Environment(extensions=extensions)
#    env.filters['jsonify'] = json.dumps
#    return env
#
#def gather_data(data_files):
#    for filename in data:
#        if filename.endswith('.json'):
#import
#        with open(filename, 'r') as fd:

def get_entry_point(group, name):
    print('get_entry_point({0}, {1})'.format(group, name))
    for entry_point in pkr.iter_entry_points(group, name):
        return entry_point.load()
    return None

def get_engine(name):
    return get_entry_point('contemplate_engine_v1', name)

def get_data(datasource):
    """
    format is key=ds:source
    """
    res = re.match('^((\w+)=)?(\w+):(\S*)$', datasource)
    if not res:
        raise ValueError('not a valid datasource: {0}'.format(datasource))
    _, key, name, source = res.groups()
    parser = get_entry_point('contemplate_parser_v1', name)
    if parser is None:
        raise ImportError('unable to load "{0}" parser'.format(name))
    return (key, parser(source).data())

def main(arguments=None):
    parser = argparse.ArgumentParser()
    #subparsers = parser.add_subparsers()

    parser.add_argument('-l', '--loglevel', default=logging.DEBUG)
    parser.add_argument('input_file', help='input_file')
    parser.add_argument('-o', '--output-file',
                        metavar='output_file', help='output file')
    parser.add_argument('-e', '--engine', default='format',
                        help='the template engine to use')
    parser.add_argument('-d', '--data', action='append', default=[],
                        metavar='data_source', help='data source')

    args = parser.parse_args(arguments)

    # Engine
    engine = get_engine(args.engine)
    print('engine={0}'.format(engine))

    # Payload
    payload = {}
    for data_source in args.data:
        key, value = get_data(data_source)
        if key:
            if key in payload:
                raise ValueError('data key "{0}" already in defined')
            payload.update({key: value})
        else:
            payload.update(value)
    print('payload={0}'.format(payload))

    # Render
    with open(args.input_file, 'r') as fd:
        content = engine().render(fd.read(), **payload)

    if args.output_file:
        with open(args.output_file, 'w') as output_fd:
            print(content, file=output_fd)
    else:
        print(content)

if __name__ == '__main__':
    main()
