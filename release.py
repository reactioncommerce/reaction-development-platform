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

CORE_MEMBERS = ['akarshitwal@gmail.com', 'jessica.wolvington@gmail.com', 'support@github.com']
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
    for author, commit, pullNumber in commits:
        if commit.lower().startswith('feat'):
            return 'minor'
    return 'patch'

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
        changelogDict[key] += '\n - ' + commit.split('\n')[0] + f' ([#{pullNumber}](https://github.com/reactioncommerce/{repo}/pull/{pullNumber}))'

    changelogDoc = sorted(map(lambda item: (categoriesOrder[categoriesDict[item[0]]], f'\n\n## {categoriesDict[item[0]]}\n{item[1]}'), changelogDict.items()))
    changelogDoc = ''.join([v for k, v in changelogDoc])
    if contributors:
        changelogDoc += f'\n\n## Contributors\n\n Special thanks to {", ".join(contributors)} for contributing to the release!'

    return f'# v{version}\n\n{repo} v{version} adds {bump} features or bug fixes and contains no breaking changes since v{str(prevVersion)}.{changelogDoc}\n\n'

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
    # npm i
    manager = 'yarn' if repo == 'example-storefront' else 'npm'
    print(f"## Running {manager} install")
    process = subprocess.Popen(f'{manager} install',
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
    bareCommits = list(gitRepo.iter_commits(f'HEAD...v{prevVersion}'))
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

def approvePR():
    print("## Approving PR")
    process = subprocess.Popen(f'gh pr review --approve',
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
        print(stdout, stderr)
        if 'passing' in str(stdout):
            return True
        elif 'failed' in str(stdout):
            print("The PR failed the build")
            return False
        print("Ask the reviewer to approve the PR")
        time.sleep(5)
        
    print(stdout)
    print(stderr)
    
def mergePR(URL):
    print("## Merging PR on github")
    process = subprocess.Popen(f'gh pr merge {URL} -m -d',
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
        print(buildItems)
    buildItem = buildItems[0]

    # Get Status of build
    while True:
        r = requests.get(f"https://circleci.com/api/v2/pipeline/{buildItem['id']}/workflow", headers=headers)
        workflowItem = r.json()['items'][0]
        print(workflowItem)
        if workflowItem['status'] == 'success':
            return True
        if workflowItem['status'] in ["failed", "error", "failing", "canceled", "unauthorized"]:
            return False
        # check after a minute
        time.sleep(60)

def updateFiles(changelogDoc, prevVersion, version):
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

def releaseRepos():
    for repo in repos:
        # Go inside the repo
        with cd(repo):
            prepareTrunk()
            
            prevVersion = getPrevVersion()
            # Get commits
            commits = getCommits(repo, prevVersion)
            if not commits:
                continue
            allCommits.extend(commits)

            print("## Getting log messages")

            # create the next version
            version = getVersion(prevVersion, commits)

            repoVersions[repo] = (str(prevVersion), str(version))
            continue
            bump = getBump(commits)
            print("Next version is", version)

            changelogDoc = generateChangelog(commits, version, bump, prevVersion, repo)
            print(changelogDoc)

            updateFiles(changelogDoc, prevVersion, version)
            files = ['CHANGELOG.md', 'docker-compose.yml', 'package.json']
            if repo != 'example-storefront':
                files.append('package-lock.json')

            URL = createPR(repo, version, files, changelogDoc)
            waitForChecks()
            mergePR(URL)
            waitForBuild(repo)
            updateDockerHub(repo, version)
            createRelease(version, changelogDoc)
            restoreTrunk()

def updateGitOps(devVersion):
    files = []
    changelog = ''
    repo = 'reaction-gitops'
    with cd(repo):
        prepareTrunk('master')
        for repo, (prevVersion, version) in repoVersions.items():
            if repo == 'example-storefront':
                # example-storefront is automatically updated
                continue
            print(f"## Updating version for {repo}")
            file = f'kustomize/{repo}/overlays/acme/kustomization.yaml'
            changelog += f'\n - {repo}-v{version}'
            files.append(file)
            with fileinput.FileInput(file, inplace=True) as file:
                for line in file:
                    print(line.replace(f'newTag: release-next-v{prevVersion}', f'newTag: release-next-v{version}'), end='')

        createPR(repo, devVersion, files, changelog, QA, branch='master')

        restoreTrunk()

def updateDevPlatform():
    prepareTrunk()
    prevVersion = getPrevVersion()
    version = getVersion(prevVersion, allCommits)
    bump = getBump(allCommits)
    print("Next version of reaction-dev-platform is", version)

    allRepos = list(repoVersions.items()) + [('reaction-development-platform', (prevVersion, version))]
    # add dev platform to all repos
    for repo, (prevVersion, ver) in allRepos:
        with fileinput.FileInput('README.md', inplace=True) as file:
            for line in file:
                print(line.replace(f'[`{prevVersion}`](https://github.com/reactioncommerce/{repo}/tree/v{prevVersion})', f'[`{ver}`](https://github.com/reactioncommerce/{repo}/tree/v{ver})'), end='')
    releases = ", ".join(map(lambda repoVersionTuple: f'[{repoVersionTuple[0]} v{repoVersionTuple[1][1]}](https://github.com/reactioncommerce/{repoVersionTuple[0]}/releases/tag/v{repoVersionTuple[1][1]})', repoVersions.items()))
    changelogDoc = f'# v{str(ver)}\nThis release is coordinated with the release of {releases} to keep the `reaction-development-platform` up-to-date with the latest version of all our development platform projects.\n'

    # Send changelog to the file
    print("## Writing changelog to file")
    line_prepender('CHANGELOG.md', changelogDoc)

    destConfig = f'./config/reaction-oss/reaction-v{str(version)}'

    # archive config file
    print("## archiving config file")
    copyfile(f'./config/reaction-oss/reaction-v{str(prevVersion)}.mk', destConfig)
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

    if not os.environ['GITHUB_TOKEN_RELEASE']:
        print("Error: Please export yout GithubKey key as GITHUB_TOKEN_RELEASE")
        sys.exit()

def main():
    prerequisite()
    releaseRepos()
    devVersion = updateDevPlatform()
    updateGitOps(devVersion)

if __name__ == "__main__":
    main()