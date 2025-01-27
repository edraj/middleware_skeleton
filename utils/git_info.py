import subprocess


def git_info():
    branch_cmd = "git rev-parse --abbrev-ref HEAD"
    result, _ = subprocess.Popen(branch_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    branch = None if result is None or len(result) == 0 else result.decode().strip()

    version_cmd = "git rev-parse --short HEAD"
    result, _ = subprocess.Popen(version_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    version = None if result is None or len(result) == 0 else result.decode().strip()

    tag_cmd = "git describe --tags"
    result, _ = subprocess.Popen(tag_cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    tag = None if result is None or len(result) == 0 else result.decode().strip()

    version_date_cmd = "git show --pretty=format:'%ad'"
    result, _ = subprocess.Popen(version_date_cmd.split(" "), stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).communicate()
    version_date = None if result is None or len(result) == 0 else result.decode().split("\n")[0]

    return {
        "commit_hash": version,
        "date": version_date,
        "branch": branch,
        "tag": tag
    }