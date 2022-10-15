from glob import glob
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pprint import pprint


def yaml_format(content: dict, indent=0) -> str:
    """
    Convert a dictionary to a YAML formatted string with the correct indentation

    :param content: The content to convert
    :param indent: The number of spaces to start indent
    :return: The formatted YAML string
    """
    dump = yaml.dump(content)
    res = ''

    for line in dump.split('\n'):
        res += ' ' * indent + line + '\n'

    return res.rstrip('\n')


def get_files():
    files = glob('add-ons/*/*.yaml')

    addons = {}

    for file in files:
        if 'aws-otel' in file:
            continue
        else:
            key = file.split('/')[1]

            addons.setdefault(key, {'chart': {}, 'values': {}})

            if 'Chart.yaml' in file:
                with open(file, 'r') as infile:
                    contents = yaml.safe_load(infile)

                chart = {
                    'name': contents['name'],
                    'description': contents['description'],
                    'dependencies': contents['dependencies'],
                }

                if str(contents.get('version')) != '0.1.0':
                    chart['version'] = contents['version']

                if str(contents.get('appVersion')) != '1.0':
                    chart['appVersion'] = contents['appVersion']

                addons[key]['chart'] = chart

            if 'values.yaml' in file:
                with open(file, 'r') as infile:
                    contents = yaml.safe_load(infile)

                values = contents[key]
                addons[key]['values'] = values

    output = [{'name': k, 'chart': v['chart'], '_values': v['values']} for k, v in addons.items()]
    pprint(output)

    environment = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        )
    environment.filters['yaml_format'] = yaml_format
    template = environment.get_template("temp.yaml")
    content = template.render(addons=output)

    with open('values.yaml', mode="w", encoding="utf-8") as message:
        message.write(content)


if __name__ == '__main__':
    get_files()
