# pipupdater

This is a small command-line tool designed for automatically updating outdated pip packages. The basic functionality is to use the output of `pip list --outdated` to update any out-of-date packages.

This tool doesn't account for dependency conflicts and doesn't yet have any functionality for tracking what dependencies pip might have updated or installed itself.

## Requirements & installation

pipupdater can be installed by downloading the `.tar.gz` or `.whl` asset from the [latest release](https://github.com/MollyMaclachlan/pipupdater/releases) and instructing pip to install the package, like so: `pip install pipupdater-x.y.z.tar.gz`. It can be updated in the same way, passing the `-U` argument to the installation command.

You can run the program simply by entering `pipupdater` in the console; it will run the `pip list --outdated` command as a subprocess to see which packages are out of date, and then proceed to update them. Any packages that fail to be updated will show up as error logs.

pipupdater's logs go to `~/.config/pipupdater/logs` on Linux and macOS, and `%APPDATA%\Roaming\pipupdater\logs` on Windows.

## Roadmap

Here's a list of things I plan to add or at least look into adding:

- [ ] Include dependencies pip installs/updates in log of updated packages
- [x] A log message when no packages need updated (at the moment it just looks like nothing happened)
- [x] A proper setup file
- [x] Allow running as a single command
- [x] Properly capture & hide terminal output from pip commands
- [x] User config options
- [ ] Dependency conflict management? (maybe) (possibly)
