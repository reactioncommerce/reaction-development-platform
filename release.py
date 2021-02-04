import subprocess
import semantic_version
import os
from collections import defaultdict
from git import Repo
import fileinput

CORE_MEMBERS = ['akarshitwal@gmail.com', 'jessica.wolvington@gmail.com']
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

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
        if '@mailchimp.com' not in author.email or author.email.lower() not in CORE_MEMBERS:
            contributors.append(author.name)
        key = commit[0].split(':')[0].lower()
        changelogDict[key] += '\n'.join(map(lambda c: ' - ' + c.strip('\n') + f' ([{pullNumber}](https://github.com/reactioncommerce/{repo}/pull/{pullNumber}))', commit)) + '\n'

    # print(changelogDict.items())
    changelogDoc = sorted(map(lambda item: (categoriesOrder[categoriesDict[item[0]]], f'\n\n## {categoriesDict[item[0]]}\n\n{item[1]}'), changelogDict.items()))
    changelogDoc = ''.join([v for k, v in changelogDoc])
    if contributors:
        changelogDoc += f'\n\n## Contributors\n\n Special thanks to {", ".join(contributors)} for contributing to the release!'

    return f'# v{version}\n\nReaction v{version} adds {bump} features or bug fixes and contains no breaking changes since v{str(prevVersion)}.{changelogDoc}\n\n'

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line + content)


repos = ['reaction-admin', 'reaction', 'example-storefront', 'reaction-identity', 'reaction-hydra']
repoVersions = {}
for repo in repos:
    # Go inside the repo
    with cd(repo):
        gitRepo = Repo()
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
            break

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

        # Get commits

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
                messages.append('\n'.join(message.split('\n')[2:]))
            else:
                messages.append(message)
            currAuthor = c.author
        if messages:
            commits.append((currAuthor, messages, pullNumber))
        if not commits:
            repoVersions[repo] = str(prevVersion)
            continue

        print("## Getting log messages")

        # create the next version
        version = getVersion(prevVersion, commits)
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
        process = subprocess.Popen('git add CHANGELOG.md docker-compose.yml package.json package-lock.json',
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
        print("Cmd id")
        print(f'gh pr create --title "Release v{version}" --base trunk --body {changelogDoc}')
         # Making PR on github
        print("## Making PR on github")
        process = subprocess.Popen(f'gh pr create --title "Release v{version}" --base trunk --body "{changelogDoc}"',
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        print(stdout)
        print(stderr)

        


        

