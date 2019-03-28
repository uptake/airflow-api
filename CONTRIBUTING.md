# Contributing to airflow-api
**WIP**

The primary goal of this guide is to help you contribute to `airflow-api` as quickly and as easily possible. It's secondary goal is to document important information for maintainers.

#### Table of contents

* [Creating an Issue](#issues)
* [Submitting a Pull Request](#prs)
* [Running Tests Locally](#testing)
* [Releasing to PyPi (WIP for maintainer)](#release)

## Creating an Issue <a name="issues"></a>

To report bugs, request features, or ask questions about the structure of the code, please [open an issue](https://github.com/UptakeOpenSource/airflow-api/issues).

### Bug Reports

If you are reporting a bug, please describe as many as possible of the following items in your issue:

- your operating system (type and version)
- your version of python
- your version of `apache-airflow`
- your `airflow.cfg` with sensitive information removed

The text of your issue should answer the question "what did you expect `airflow-api` to do and what did it actually do?".

We welcome any and all bug reports. However, we'll be best able to help you if you can reduce the bug down to a **minimum working example**. A **minimal working example (MWE)** is the minimal code needed to reproduce the incorrect behavior you are reporting. Please consider the [stackoverflow guide on MWE authoring](https://stackoverflow.com/help/mcve).

If you're interested in submitting a pull request to address the bug you're reporting, please indicate that in the issue.

### Feature Requests

We welcome feature requests, and prefer the issues page as a place to log and categorize them. If you would like to request a new feature, please open an issue there and add the `enhancement` tag.

Good feature requests will note all of the following:

- what you would like to do with `airflow-api`
- how valuable you think being able to do that with `airflow-api` would be
- sample code showing how you would use this feature if it was added

If you're interested in submitting a pull request to address the bug you're reporting, please indicate that in the issue.

## Submitting a Pull Request <a name="prs"></a>

We welcome [pull requests](https://help.github.com/articles/about-pull-requests/) from anyone interested in contributing to `airflow-api`. This section describes best practices for submitting PRs to this project.

If you are interested in making changes that impact the way `airflow-api` works, please [open an issue](#issues) proposing what you would like to work on before you spend time creating a PR.

If you would like to make changes that do not directly impact how `airflow-api` works, such as improving documentation, adding unit tests, or minor bug fixes, please feel free to implement those changes and directly create PRs.

If you are not sure which of the preceding conditions applies to you, open an issue. We'd love to hear your idea!

To submit a PR, please follow these steps:

1. Fork `airflow-api` to your GitHub account
2. Create a branch on your fork and add your changes
3. If you are changing or adding to the python code in the package, add unit tests and integration tests confirming that your code works as expected
3. When you are ready, click "Compare & Pull Request". Open A PR comparing your branch to the `master` branch in this repo
4. In the description section on your PR, please indicate the following:
    - description of what the PR is trying to do and how it improves `airflow-api`
    - links to any open [issues](https://github.com/UptakeOpenSource/airflow-api/issues) that your PR is addressing

We will try to review PRs promptly and get back to you within a few days.

## Running Tests Locally <a name="testing"></a>

### Development
In order to do development you will need a python 3.6 environment set up as your base python installation.

We encourage developers to understand and leverage either of the following to create a clean environment for 
development:
* [conda](https://docs.conda.io/en/latest/) via [Anaconda](https://www.anaconda.com/) 
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)

You will also need [docker](https://www.docker.com/products/docker-desktop) installed to run integration tests

### Running Unit Tests
To run all tests simply run the following command:

    ./bin/run_tests.sh
    
### Running Integration Tests
This assumes you are developing on Mac OSX System. Development on other systems is currently not tested or documented.

You will need docker installed on your system in order to run these tests.

You will first need to build the base image used in testing. This helps speed up development by establishing system
values which aren't often changed. You can do so by running the following command:

    docker build -f AirflowTestEnvDockerfile -t "airflow-api:base-image" .

You will need to add the following to your /etc/hosts file:

    127.0.0.1       airflow-webserver
    
This can be done easily bu running the following command:

    sudo echo "127.0.0.1 airflow-webserver" >> /etc/hosts 
 
To run all tests simply run the following command:

    ./bin/run_integration_tests.sh
    
If you would like to run tests in debug mode you can run the following to spin up the docker images needed:

    ./docker-compose-wrapper.sh up
    
When you are done with the images you can spin them down with this command:

    ./docker-compose-wrapper.sh down

## Releasing to PyPi (for maintainer) <a name="release"></a>
**WIP**

Once substantial time has passed or significant changes have been made to `airflow-api`, a new release should be pushed to [pypi](https://pypi.org/). 

This is the exclusively the responsibility of the package maintainer, but is documented here for our own reference and to reflect the consensus reached between the maintainer and other contributors.

This is a manual process, with the following steps.

### Open a PR

**WIP**

Open a PR with a branch name `release/v0.0.0` (replacing 0.0.0 with the actual version number).

Add a section for this release to `NEWS.md`.  This file details the new features, changes, and bug fixes that occured since the last version.  

Add a section for this release to `pypi-comments.md`. This file holds details of our submission comments to PyPi and their responses to our submissions.  

Change the `version` value in `/airflow-api/version.py` to the official version you want on CRAN.

This project uses Github Pages to host a documentation site:

https://uptakeopensource.github.io/airflow-api/


### Submit to PyPi

**TBD**

### Handle feedback from PyPi

**WIP**

The maintainer will get an email from CRAN with the status of the submission. 

If the submission is not accepted, do whatever CRAN asked you to do. Update `pypi-comments.md` with some comments explaining the requested changes. Repeat this process until the package gets accepted.

### Merge the PR
**WIP**

Once the submission is accepted, great! Update `pypi-comments.md` and merge the PR.

### Create a Release on GitHub
**WIP**

We use [the releases section](https://github.com/UptakeOpenSource/airflow-api/releases) in the repo to categorize certain important commits as release checkpoints. This makes it easier for developers to associate changes in the source code with the release history on PyPi.

Navigate to https://github.com/UptakeOpenSource/airflow-api/releases/new. Click the dropdown in the "target" section, then click "recent commits". Choose the latest commit for the release PR you just merged. This will automatically create a [git tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on that commit and tell Github which revision to build when people ask for a given release.

Add some notes explaining what has changed since the previous release.

### Open a new PR to begin development on the next version
**WIP**

Now that everything is done, the last thing you have to do is move the repo ahead of the version you just pushed to PyPi.

Make a PR that adds a `.9000` on the end of the version you just released. This is a common practice in open source software development. It makes it obvious that the code in source control is newer than what's available from package managers, but doesn't interfere with the [semantic versioning](https://semver.org/) components of the package version.