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

CORE_MEMBERS = ['akarshitwal@gmail.com', 'jessica.wolvington@gmail.com']
QA = 'manueldelreal'
repos = [
    'reaction-admin',
    'reaction', 
    'example-storefront', 
    'reaction-identity'
    ]
dockerRepoDict = {
    'reaction-admin': 'admin',
    'reaction': 'reaction',
    'reaction-identity': 'identity',
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
    for author, commit, pullNumber in commits:
        if commit[0].lower().startswith('feat'):
            return 'major'
    return 'minor'

def getVersion(prevVersion, commits):
    if prevVersion.prerelease:
        # only increment the build version
        nextVersion = semantic_version.Version(major=prevVersion.major, minor=prevVersion.minor, patch=prevVersion.patch, prerelease=(prevVersion.prerelease[0], str(int(prevVersion.prerelease[1]) + 1) ))
    else:
        bump = getBump(commits)
        if bump == 'minor':
            nextVersion = prevVersion.next_minor()
        else:
            nextVersion = prevVersion.next_patch()
    return str(nextVersion)

def generateChangelog(commits, version, bump, prevVersion, repo):
    categoriesOrder = {
        'Feature': 0,
        'Fixes': 0,
        'Refactors': 0,
        'Tests': 0,
        'Chore: 0'
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
    contributors = []
    for author, commit, pullNumber in commits:
        key = ''
        if not author.email.lower().endswith('@mailchimp.com') and author.email.lower() not in CORE_MEMBERS:
            contributors.append(author.name)
        key = commit[0].split(':')[0].lower()
        changelogDict[key] += '\n'.join(map(lambda c: ' - ' + c.strip('\n') + f' ([{pullNumber}](https://github.com/reactioncommerce/{repo}/pull/{pullNumber}))', commit))

    # print(changelogDict.items())
    changelogDoc = sorted(map(lambda item: (categoriesOrder[categoriesDict[item[0]]], f'\n\n## {categoriesDict[item[0]]}\n\n{item[1]}'), changelogDict.items()))
    changelogDoc = ''.join([v for k, v in changelogDoc])
    if contributors:
        changelogDoc += f'\n\n## Contributors\n\n Special thanks to {", ".join(contributors)} for contributing to the release!'

    return f'# v{version}\n\nReaction v{version} adds {bump} features or bug fixes and contains no breaking changes since v{str(prevVersion)}.{changelogDoc}\n\n'

def getPrevVersion():
    # Get latest relase tag name
    process = subprocess.Popen(['git', 'describe', '--abbrev=0', '--tags'],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    tag, stderr = process.communicate()
    tag = tag.decode("utf-8").strip('\n')
    prevVersion = semantic_version.Version(tag[1:])
    print(f"Previous release was {tag}")
    if stderr:
        print(stderr)
        print("Error getting tag")
    return prevVersion      

def prepareTrunk():
    #  Stashing the changes
    print("## Stashing the changes")
    process = subprocess.Popen('git stash',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # Change branch to trunk
    print("## Running git checkout trunk")
    process = subprocess.Popen(['git', 'checkout', 'trunk'],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    
    # Pull the latest changes
    print("## Running git pull")
    process = subprocess.Popen(['git', 'pull'],
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
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def createPR(version, files, changelogDoc, reviewer='reactioncommerce/oc'):
    # npm i
    print("## Running npm install")
    process = subprocess.Popen('npm install',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # create new brach
    print("## Creating release branch locally")
    process = subprocess.Popen(f'git checkout -b release-next-v{version}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # staging files
    print("## Staging files")
    process = subprocess.Popen(f'git add {" ".join(files)}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    # commiting files
    print("## Comitting files")
    process = subprocess.Popen(f'git commit -m "Release v{version}" --signoff',
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
    print(f'gh pr create --title "Release v{version}" --base trunk --body {changelogDoc} --reviewer {reviewer}')
        # Making PR on github
    print("## Making PR on github")
    process = subprocess.Popen(f'gh pr create --title "Release v{version}" --base trunk --body "{changelogDoc}"  --reviewer {reviewer}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)


def getCommits(gitRepo, prevVersion):
    bareCommits = list(gitRepo.iter_commits(f'HEAD...v{prevVersion}'))
    commits = []
    messages = []
    currAuthor = ''
    pullNumber = ''
    for index, c in enumerate(bareCommits):
        # XXX: Strip new lines not working
        message = '\n'.join(filter(lambda msg: 'Signed-off-by:' not in msg, c.message.strip('\n').strip('\t').split('\n')))
        if message.startswith("Merge pull request"):
            if messages:
                commits.append((currAuthor, messages, pullNumber))
                messages = []
            pullNumber = message.split(' ')[3]
        else:
            messages.append(message)
        currAuthor = c.author
    if messages:
        commits.append((currAuthor, messages, pullNumber))
    return commits

def createRelease(version, changelogDoc):
    print("## Creating release on github")
    process = subprocess.Popen(f'gh release create v{version} -n {changelogDoc} -d -t v{version}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def waitForChecks():
    print("## Waiting for the build process")
    while True:
        process = subprocess.Popen(f'gh pr status | grep "Current" -A 2 | tail -1',
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        if 'passing' in stdout:
            return True
        elif 'failed' in stdout:
            print("The PR failed the build")
            return False
        time.sleep(5)
        
    print(stdout)
    print(stderr)
    
def mergePR(URL):
    print("## Merging PR on github")
    process = subprocess.Popen(f'gh pr merge {URL} -d',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def waitForBuild(repo):
    headers = {'Circle-Token': os.environ['CIRCLE_TOKEN']}
    buildItems = []
    payload = {
        'org-slug': 'gh/reactioncommerce'
    }
    pageToken = None
    while not buildItems:
        if pageToken:
            payload['page-token'] = pageToken
        r = requests.get("https://circleci.com/api/v2/pipeline", params=payload, headers=headers)
        piplelines = r.json()
        buildItems = list(filter(lambda item: item['project_slug'] == f'gh/reactioncommerce/{repo}' and 'tag' not in item['vcs'] and item['vcs']['branch'] == 'trunk' , piplelines['items']))
        pageToken = piplelines['next_page_token']
    buildItem = buildItems[0]

    # Get Status of build
    while True:
        r = requests.get(f"https://circleci.com/api/v2/pipeline/{buildItem['id']}/workflow", headers=headers)
        workflowItem = r.json()['items'][0]
        if workflowItem['status'] == 'success':
            return True
        if workflowItem['status'] in ["failed", "error", "failing", "canceled", "unauthorized"]:
            return False
        # check after a minute
        time.sleep(60)

def releaseRepos():
    for repo in repos:
        # Go inside the repo
        with cd(repo):
            prepareTrunk()
            gitRepo = Repo()
            
            prevVersion = getPrevVersion()
            # Get commits
            commits = getCommits(gitRepo, prevVersion)
            if not commits:
                continue
            allCommits.extend(commits)

            print("## Getting log messages")

            # create the next version
            version = getVersion(prevVersion, commits)
            repoVersions[repo] = (str(prevVersion), str(version))
            bump = getBump(commits)
            print("Next version is", version)

            changelogDoc = generateChangelog(commits, version, bump, prevVersion, repo)
            print(changelogDoc)

            # Send changelog to the file
            print("## Writing changelog to file")
            line_prepender('CHANGELOG.md', changelogDoc)

            print("## Writing version to package.json")
            with fileinput.FileInput('package.json', inplace=True) as file:
                for line in file:
                    print(line.replace(f'"version": "{str(prevVersion)}"', f'"version": "{version}"'), end='')

            print("## Writing version to docker-compose.yml")
            with fileinput.FileInput('docker-compose.yml', inplace=True) as file:
                for line in file:
                    print(line.replace(str(prevVersion), version), end='')

            files = ['CHANGELOG.md', 'docker-compose.yml', 'package.json', 'package-lock.json']
            createPR(version, files, changelogDoc)
            waitForChecks()
            mergePR()
            waitForBuild()
            updateDockerHub()
            createRelease(version, changelogDoc)
            restoreTrunk()

def updateGitOps(repoVersions, devVersion):
    files = []
    changelog = ''
    with cd('reaction-gitops'):
        for repo, (prevVersion, version) in repoVersions.items():
            print(f"## Updating version for {repo}")
            file = f'kustomize/{repo}/overlays/acme/kustomization.yaml'
            changelog += f'\n - {repo}-v{version}'
            files.append(file)
            with fileinput.FileInput(file, inplace=True) as file:
                for line in file:
                    print(line.replace(f'newTag: release-next-v{prevVersion}', f'newTag: release-next-v{version}'), end='')

    prepareTrunk()

    createPR(devVersion, files, changelog)

    restoreTrunk()

def updateDevPlatform():
    prevVersion = getPrevVersion()
    version = getVersion(prevVersion, allCommits)

    allRepos = repoVersions.items() + [('reaction-development-platform', (prevVersion, version))]
    # add dev platform to all repos
    for repo, (prevVersion, version) in allRepos:
        with fileinput.FileInput('README.md', inplace=True) as file:
            for line in file:
                print(line.replace(f'[`{prevVersion}`](https://github.com/reactioncommerce/{repo}/tree/v{prevVersion})', f'[`{version}`](https://github.com/reactioncommerce/{repo}/tree/v{version})'), end='')
    releases = ", ".join(map(lambda repo, v: f'[{repo} v{v[1]}(https://github.com/reactioncommerce/{repo}/releases/tag/v{v[1]})]', repoVersions.items()))
    changelogDoc = f'# v{str(version)}\nThis release is coordinated with the release of {releases} to keep the `reaction-development-platform` up-to-date with the latest version of all our development platform projects.\n'

    # Send changelog to the file
    print("## Writing changelog to file")
    line_prepender('CHANGELOG.md', changelogDoc)

    destConfig = f'./config/reaction-oss/reaction-v{str(version)}'

    # archive config file
    print("## archiving config file")
    copyfile(f'./config/reaction-oss/reaction-v{str(prevVersion)}', destConfig)
    for repo, (prevVersion, version) in repoVersions.items():
        with fileinput.FileInput(destConfig, inplace=True) as file:
            for line in file:
                print(line.replace(f'{repo},v{str(prevVersion)}', f'{repo},v{str(version)}'), end='')

    # updating the config file
    print("## updating config file")
    for repo, (prevVersion, version) in repoVersions.items():
        with fileinput.FileInput('config.mk', inplace=True) as file:
            for line in file:
                print(line.replace(f'{repo},v{str(prevVersion)}', f'{repo},v{str(version)}'), end='')


    prepareTrunk()

    files = ['README.md', 'CHANGELOG.md', 'config.mk', destConfig]
    createPR(version, files, changelogDoc, QA)

    restoreTrunk()
    return version

def updateDockerHub(repo, version):
    dockerRepo = dockerRepoDict[repo]

    print("## Pulling trunk")
    process = subprocess.Popen(f'docker pull reactioncommerce/{dockerRepo}:trunk',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    print("## Renaming tag")
    process = subprocess.Popen(f'docker tag reactioncommerce/{dockerRepo}:trunk reactioncommerce/{dockerRepo}:{version}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

    print("## Pushing to docker")
    process = subprocess.Popen(f'docker push reactioncommerce/{dockerRepo}:{version}',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)

def prerequisite():
    # Current directory should be reaction-development-platform
    pwd = os.getcwd()
    if not pwd.endswith('reaction-development-platform'):
        print("Error: Please run the script from reaction-development-platform")
        sys.exit()
    # gitops repos must be present
    subdirs = [name for name in os.listdir(".") if os.path.isdir(name)]
    if 'reaction-gitops' not in subdirs:
        print("Error: Please clone reaction-gitops in reaction-development-platform")
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

def main():
    prerequisite()
    releaseRepos()
    devVersion = updateDevPlatform()
    updateGitOps(devVersion)

if __name__ == "__main__":
    main()