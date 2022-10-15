import os
from enum import Enum

import yaml
from jinja2 import Environment, PackageLoader, select_autoescape


class AddonFileType(Enum):
    """The two different add-on file types"""

    Chart = 'Chart'
    Values = 'values'


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


def write_addon_file(template, name: str, values: dict, file_type: AddonFileType) -> None:
    """
    Generate and write the add-on file to disk under the `add-ons/<add-on name>/` directory

    :param template: The template to use when rendering the file
    :param name: The name of the chart/add-on
    :param values: The values for the chart/add-on
    :param file_type: The type of file to generate (`Chart.yaml` or `values.yaml`)
    :return: None
    """
    if file_type is AddonFileType.Chart:
        values = {
            'name': name,
            **values.get('chart', {}),
        }

    if file_type is AddonFileType.Values:
        # Values are just splat out under the name unlike the `Chart.yaml` file
        values = {
            'name': name,
            'values': values.get('values', {}),
        }

    content = template.render(values)

    with open(f'add-ons/{name}/{file_type.value}.yaml', mode='w', encoding='utf-8') as message:
        # Ensure only one trailing newline
        message.write(f'{content.rstrip()}\n')


def template() -> None:
    """
    Render the `add-ons/` and `chart/` directory contents based on values provided in `values.yaml`
    """
    env = Environment(
        loader=PackageLoader('template'),
        autoescape=select_autoescape(),
        keep_trailing_newline=True,
    )
    # Add custom formatter
    env.filters['yaml_format'] = yaml_format

    addon_chart_template = env.get_template('add-ons/Chart.yaml')
    addon_values_template = env.get_template('add-ons/values.yaml')

    with open('values.yaml', 'r') as valuesfile:
        values = yaml.safe_load(valuesfile)

        for addon in values['addons']:
            for chart_name, chart_values in addon.items():
                # Create directory if it doesn't exist
                file_directory = os.path.dirname(f'./add-ons/{chart_name}/')
                if not os.path.exists(file_directory):
                    os.makedirs(file_directory)

                write_addon_file(
                    template=addon_chart_template,
                    name=chart_name,
                    values=chart_values,
                    file_type=AddonFileType.Chart,
                )
                write_addon_file(
                    template=addon_values_template,
                    name=chart_name,
                    values=chart_values,
                    file_type=AddonFileType.Values,
                )


if __name__ == '__main__':
    template()
