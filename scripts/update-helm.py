import os
import glob
import yaml
import sys
import subprocess
from packaging import version
import requests


def compare_versions(current_version, latest_version, chart_name):
    # Compare the versions
    if latest_version and version.parse(latest_version) > version.parse(current_version):
        print(
            f"Newer version available for {chart_name}: {latest_version} (current: {current_version})")
        return latest_version
    # else:
    #    print(f"No newer version available for {chart_name} (current: {current_version})")
    return None


def extract_values(yaml_file):
    with open(yaml_file, 'r') as file:
        content = yaml.safe_load(file)
        try:
            addon_chart = content['spec']['generators'][0]['merge']['generators'][0]['clusters']['values']['addonChart']
            addon_chart_version = content['spec']['generators'][0]['merge'][
                'generators'][0]['clusters']['values']['addonChartVersion']
            addon_chart_repository = content['spec']['generators'][0]['merge'][
                'generators'][0]['clusters']['values']['addonChartRepository']
            return addon_chart, addon_chart_version, addon_chart_repository
        except (KeyError, TypeError):
            # print(f"Unable to extract values from {yaml_file}")
            return None, None, None


def check_newer_version(repo_url, chart_name, current_version):
    # Remove the repository
    subprocess.run(['helm', 'repo', 'remove', 'temp_repo'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Add the repository
    subprocess.run(['helm', 'repo', 'add', 'temp_repo', repo_url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Update the repository
    # hide output to not spam the console
    subprocess.run(['helm', 'repo', 'update'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Fetch the latest version of the chart
    # print(f"Fetching latest version for {chart_name} from {repo_url}")
    latest_version_output = subprocess.getoutput(
         f'helm search repo temp_repo/{chart_name} -o yaml')
    parsed_output = yaml.safe_load(latest_version_output)
    latest_version = parsed_output[0]['version']
    # print(f"Current version for {chart_name}: {current_version}")

    update_version = compare_versions(
        current_version, latest_version, chart_name)
    # Remove the repository
    subprocess.run(['helm', 'repo', 'remove', 'temp_repo'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return update_version


def check_newer_version_from_github(owner, repo, current_version):
    latest_version = get_latest_github_release_version(owner, repo)
    # print(f"Current version for {owner}/{repo}: {current_version}")
    # print(f"Latest release version for {owner}/{repo}: {latest_version}")
    return compare_versions(current_version, latest_version, repo)


def get_latest_github_release_version(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)

    if response.status_code != 200:
        print(
            f"Error fetching latest release for {owner}/{repo}: {response.status_code}")
        return None

    release_info = response.json()
    return release_info.get("tag_name", None)

# write function to update the version in the yaml file with updated version


def update_version(yaml_file, current_version, update_version):
    # If update_version is not None, update the version in the yaml file
    if update_version is None:
        return None
    # update the yaml_file without parsing as yaml, and just find current_version and replace it with update_version without changing anything about the file
    with open(yaml_file, 'r') as file:
        lines = file.readlines()
        # Replace the current_version with the update_version in each line
        updated_lines = [line.replace(current_version, update_version) for line in lines]
    # Write the updated lines back to the file
    with open(yaml_file, 'w') as file:
        file.writelines(updated_lines)


# main
if len(sys.argv) < 2:
    print("Please provide the directory path as an argument.")
    sys.exit(1)

directory_path = sys.argv[1]
yaml_files = glob.glob(os.path.join(
    directory_path, '**/*.yaml'), recursive=True)

for yaml_file in yaml_files:
    addon_chart, addon_chart_version, addon_chart_repository = extract_values(
        yaml_file)
    if addon_chart is not None:
        if addon_chart == "karpenter":
            update_version(yaml_file, addon_chart_version, check_newer_version_from_github(
                "aws", "karpenter", addon_chart_version))
            continue
        if addon_chart == "aws-gateway-controller-chart":
            update_version(yaml_file, addon_chart_version, check_newer_version_from_github(
                "aws", "aws-application-networking-k8s", addon_chart_version))
            continue
        update_version(yaml_file, addon_chart_version, check_newer_version(
            addon_chart_repository, addon_chart, addon_chart_version))
