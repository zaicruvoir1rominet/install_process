# Contributing to ``install_process``
We want to make contributing to this project as easy and transparent as
possible.

## Our Development Process
This github repo is the source of truth and all changes need to be reviewed in
pull requests.

## Pull Requests
We actively welcome your pull requests.

### Setup Your Environment

1. Install [hatch](https://hatch.pypa.io/latest/install/)
2. Fork the repo on your side
3. Clone the repo
   > git clone [your fork.git] install_process  
   > cd install_process
5. Setup the env
   > hatch env create

You are now ready to create your own branch from main, and contribute.
Please provide tests (using unittest), and update the documentation, if applicable.

### Before Submitting Your Pull Request

1. Check linters
   > hatch run lint
2. Test your changes
   > hatch run test

## Issues

We use GitHub issues to track public bugs. Please ensure your description is
clear and has enough instructions to be able to reproduce the issue.

## License
By contributing to ``install_process``, you agree that your contributions will be licensed
under the MIT LICENSE file in the root directory of this source tree.
