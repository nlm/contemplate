from __future__ import absolute_import, print_function
import pkg_resources as pkr
import argparse
import logging
import re

def get_entry_point(group, name):
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

    parser.add_argument('-l', '--loglevel', default='WARNING',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'))
    parser.add_argument('input_file', help='input_file')
    parser.add_argument('-o', '--output-file',
                        metavar='output_file', help='output file')
    parser.add_argument('-e', '--engine', default='format',
                        help='the template engine to use')
    parser.add_argument('-d', '--data', action='append', default=[],
                        metavar='data_source', help='data source')

    args = parser.parse_args(arguments)

    logging.basicConfig(level=getattr(logging, args.loglevel))
    logger = logging.getLogger(__name__)

    # Engine
    engine = get_engine(args.engine)
    logger.debug('engine={0}'.format(engine))

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
    logger.debug('payload={0}'.format(payload))

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
