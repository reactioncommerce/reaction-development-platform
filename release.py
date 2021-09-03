'''
Make sure you follow the repos from this page: https://app.circleci.com/projects/project-dashboard/github/reactioncommerce/
'''
import subprocess
import semantic_version
import os
from collections import defaultdict
from git import Repo
import fileinput
import time
from shutil import copyfile
import sys
import requests
from github import Github
import re

CORE_MEMBERS = ['akarshitwal@gmail.com', 'support@github.com']
QA = 'manueldelreal'

repos = [
    'reaction-admin',
    'reaction', 
    'example-storefront', 
]

previousReleaseVersion = {
    'reaction-admin': '',
    'reaction': '',
    'example-storefront': '',
}

dockerRepoDict = {
    'reaction-admin': 'admin',
    'reaction': 'reaction',
    'example-storefront': 'example-storefront',
}

repoVersions = {}
# list of commits across all repos
allCommits = []

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line + content)

def getBump(commits):
    level = 'patch'
    for author, commit, pullNumber in commits:
        if commit.lower().startswith('feat'):
            ## its minor if not already major
            if level != 'major':
                level = 'minor'
        if 'BREAKING CHANGE:' in commit:
            return 'major'
    return 'patch'

def getVersion(prevVersion, commits):
    if prevVersion.prerelease:
        # only increment the build version
        nextVersion = semantic_version.Version(major=prevVersion.major, minor=prevVersion.minor, patch=prevVersion.patch, prerelease=(prevVersion.prerelease[0], str(int(prevVersion.prerelease[1]) + 1) ))
    else:
        bump = getBump(commits)
        if bump == 'minor':
            nextVersion = prevVersion.next_minor()
        elif bump == 'major':
            nextVersion = prevVersion.next_major()
        else:
            nextVersion = prevVersion.next_patch()
    return str(nextVersion)

def generateChangelog(commits, version, bump, prevVersion, repo):
    categoriesOrder = {
        'Feature': 0,
        'Fixes': 0,
        'Refactors': 0,
        'Tests': 0,
        'Chore': 0,
        'Docs': 0,
        'Style': 0,
        'Performance': 0,
    }
    categoriesDict = {
        'feat': 'Feature',
        'fix': 'Fixes',
        'docs': 'Docs',
        'style': 'Style',
        'refactor': 'Refactors',
        'perf': 'Performance',
        'test': 'Tests',
        'chore': 'Chore',
    }
    changelogDict = defaultdict(str)
    contributors = set([])
    for author, commit, pullNumber in commits:
        authorEmail = author.email.lower()
        if not (authorEmail.endswith('@mailchimp.com') or authorEmail in CORE_MEMBERS or 'dependabot' in authorEmail):
            contributors.add(author.name)
        key = commit.split(':')[0].lower()
        if '(' in key:
            # if the key has a scope
            key = key.split('(')[0]
        if key not in categoriesDict.keys():
            # anything that is not in above is a fix
            key = 'fix'
        changelogDict[key] += '\n - ' + commit.split('\n')[0] + f' [#{pullNumber}](https://github.com/reactioncommerce/{repo}/pull/{pullNumber})'

    changelogDoc = sorted(map(lambda item: (categoriesOrder[categoriesDict[item[0]]], f'\n\n## {categoriesDict[item[0]]}\n{item[1]}'), changelogDict.items()))
    changelogDoc = ''.join([v for k, v in changelogDoc])
    if contributors:
        changelogDoc += f'\n\n## Contributors\n\n Special thanks to {", ".join(contributors)} for contributing to the release!'

    return f'# v{version}\n\n{repo} v{version} adds {bump} features or bug fixes and contains no breaking changes since v{str(prevVersion)}.{changelogDoc}\n\n'

def getLatestVersion():
    # Get latest relase tag name
    process = subprocess.Popen(['git', 'describe', '--abbrev=0', '--tags'],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    tag, stderr = process.communicate()
    tag = tag.decode("utf-8").strip('\n')
    version = semantic_version.Version(tag[1:])
    
    if stderr:
        print(stderr)
        print("Error getting tag")
    return version      

def prepareTrunk(branch='trunk'):
    #  Stashing the changes
    print("## Stashing the changes")
    process = subprocess.Popen('git stash',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # Change branch to trunk
    print(f"## Running git checkout {branch}")
    process = subprocess.Popen(['git', 'checkout', branch],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # Pull the latest changes
    print("## Running git pull")
    process = subprocess.Popen(['git', 'pull', 'origin'],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def restoreTrunk():
    #  unstashing the changes
    print("## Un-stashing the changes")
    process = subprocess.Popen('git stash apply',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def createPR(repo, version, files, changelogDoc, reviewer='reactioncommerce/oc', branch='trunk'):
    # create new brach
    print("## Creating release branch locally")
    process = subprocess.Popen(f'git checkout -b release-next-v{version}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    if 'fatal' in str(stderr):
        exit()

    # staging files
    print("## Staging files")
    process = subprocess.Popen(f'git add {" ".join(files)}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    if 'fatal' in str(stderr):
        exit()

    # commiting files
    print("## Comitting files")
    process = subprocess.Popen(f'git commit -m "ci: v{version}" --signoff',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)


    # pushing the branch to github
    print("## Pushing the branch to github")
    process = subprocess.Popen(f'git push origin HEAD',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    print(f'gh pr create --title "Release v{version}" --base {branch} --body {changelogDoc} --reviewer {reviewer}')
        # Making PR on github
    print("## Making PR on github")
    process = subprocess.Popen(f'gh pr create --title "Release v{version}" --base {branch} --body "{changelogDoc}"  --reviewer {reviewer}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    return str(stdout).strip('\n')

def getCommits(repo, prevVersion):
    gitRepo = Repo()
    user = Github(os.environ['GITHUB_TOKEN_RELEASE'])
    repo = user.get_repo(f'reactioncommerce/{repo}')
    bareCommits = list(gitRepo.iter_commits(f'HEAD...v'+str(prevVersion)))
    commits = []
    for index, c in enumerate(bareCommits):
        commit = repo.get_commit(sha=str(c))
        commitPulls = commit.get_pulls()
        pullNumber = 0
        for pull in commitPulls:
            pullNumber = pull.number
        if not pullNumber:
            continue
        message = '\n'.join(filter(lambda msg: 'Signed-off-by:' not in msg, c.message.strip('\n').strip('\t').split('\n')))
        if message.startswith("Merge "):
            # these are generate when PRs are merged.
            pass
        else:
            commits.append((c.author, message, pullNumber))
    return commits

def createRelease(version, changelogDoc):
    print("## Creating release on github")
    process = subprocess.Popen(f'gh release create v{version} -d -t v{version} -n "{changelogDoc}"',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def getCurrentRepoVersion():
    print(os.getcwd())
    for line in fileinput.FileInput('config.mk'):
        res = re.search("^https://github.com/reactioncommerce/.*,",line)
        if res:
            lineArr = line.split(",")
            previousReleaseVersion[lineArr[-2]]=lineArr[-1].replace('\\','').replace('v','').strip()

def prepareRepos():
    getCurrentRepoVersion()
    for repo in repos:
        # Go inside the repo
        with cd(repo):
            prepareTrunk()
            latestVersion = getLatestVersion()
            print("Latest version of {0} is {1}".format(repo,latestVersion))
            
            # Get commits
            commits = getCommits(repo, previousReleaseVersion[repo])
            if not commits:
                continue
            allCommits.extend(commits)
            repoVersions[repo] = (str(previousReleaseVersion[repo]), str(latestVersion))

def updateDevPlatform():
    print("Starting Reaction Development Platform update.")
    prepareTrunk()
    prevVersion = getLatestVersion()
    version = getVersion(prevVersion, allCommits)
    bump = getBump(allCommits)
    print("Next version of reaction-dev-platform is", version)

    allRepos = list(repoVersions.items()) + [('reaction-development-platform', (prevVersion, version))]
    # add dev platform to all repos
    for repo, (prevVersion, ver) in allRepos:
        print(f'Updating {repo} from {prevVersion} to {ver}')
        with fileinput.FileInput('README.md', inplace=True) as file:
            for line in file:
                print(line.replace(f'[`{prevVersion}`](https://github.com/reactioncommerce/{repo}/tree/v{prevVersion})', f'[`{ver}`](https://github.com/reactioncommerce/{repo}/tree/v{ver})'), end='')
    releases = ", ".join(map(lambda repoVersionTuple: f'[{repoVersionTuple[0]} v{repoVersionTuple[1][1]}](https://github.com/reactioncommerce/{repoVersionTuple[0]}/releases/tag/v{repoVersionTuple[1][1]})', repoVersions.items()))
    changelogDoc = f'# v{str(ver)}\nThis release is coordinated with the release of {releases} to keep the `reaction-development-platform` up-to-date with the latest version of all our development platform projects.\n'

    # Send changelog to the file
    print("## Writing changelog to file")
    line_prepender('CHANGELOG.md', changelogDoc)

    destConfig = f'./config/reaction-oss/reaction-v{str(version)}.mk'

    print("## Copying config file")
    copyfile(f'./config/reaction-oss/reaction-v{str(prevVersion)}.mk', destConfig)

    ## replacing version number at the top of the file
    with fileinput.FileInput(destConfig, inplace=True) as file:
            for line in file:
                if "Reaction OSS" in line:
                    print(f'### Reaction OSS v{version}')
                else:
                    print(line, end='')

    for repo, (prevVersion, ver) in repoVersions.items():
        with fileinput.FileInput(destConfig, inplace=True) as file:
            for line in file:
                print(line.replace(f'{repo},v{str(prevVersion)}', f'{repo},v{str(ver)}'), end='')

    # updating the config file
    print("## updating config file")
    for repo, (prevVersion, ver) in repoVersions.items():
        with fileinput.FileInput('config.mk', inplace=True) as file:
            for line in file:
                print(line.replace(f'{repo},v{str(prevVersion)}', f'{repo},v{str(ver)}'), end='')

    files = ['README.md', 'CHANGELOG.md', 'config.mk', destConfig]
    createPR('reaction-development-platform', version, files, changelogDoc, QA)

    restoreTrunk()
    return version

def prerequisite():
    # Current directory should be reaction-development-platform
    pwd = os.getcwd()
    if not pwd.endswith('reaction-development-platform'):
        print("Error: Please run the script from reaction-development-platform")
        sys.exit()  

    process = subprocess.Popen('gh --version',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if stderr:
        print("Error: github command line not installed. Please install gh")
        sys.exit()

    process = subprocess.Popen('gh auth status',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if "Logged in" not in str(stderr):
        print(stderr)
        print("Error: Please login into github using command line")
        sys.exit()

    if not os.environ['CIRCLE_TOKEN']:
        print("Error: Please export yout CircleCI key as CIRCLE_TOKEN")
        sys.exit()

    if not os.environ['GITHUB_TOKEN_RELEASE']:
        print("Error: Please export yout GithubKey key as GITHUB_TOKEN_RELEASE")
        sys.exit()


def main():
    prerequisite()
    prepareRepos()
    devVersion = updateDevPlatform()

if __name__ == "__main__":
    main()